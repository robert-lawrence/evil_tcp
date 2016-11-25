##Connection for EVIL protocol

##Connection is created and held by a socket, and held by ONE application

##Connection is responsible for maintaining the sliding window ARQ and its
##in/out buffers, as well as its own state, including termination

##when a connection is first created it is either in:
##              syn_recv (if it was created with socket.accept)
##              syn_sent (if it was created with socket.connect)

import Queue
import threading
from util import EVILPacket
from util import debugLog
import util
import time

MAX_SEND_BYTES = 800

class STATE():
    CLOSED = 1
    LISTEN = CLOSED << 1
    SYN_RECV = LISTEN << 1
    SYN_SENT = SYN_RECV << 1
    ESTABLISHED = SYN_SENT << 1
    FIN_WAIT_1 = ESTABLISHED << 1
    FIN_WAIT_2 = FIN_WAIT_1 << 1
    FIN_CLOSING = FIN_WAIT_2 << 1
    TIME_WAIT = FIN_CLOSING << 1
    CLOSE_WAIT = TIME_WAIT << 1
    LAST_ACK = CLOSE_WAIT << 1


class Connection:

    ##member variables are window size, max window size, in/out buffers, and
    ##a state enum
    DEFAULT_TIMEOUT = 5

    def __init__(self, src_port, dst_port, maxWindowSize, state, otherAddress, socket):
        self.max_window_size = maxWindowSize
        self.max_send_size = 1
        self.state = state
        self.stateCond = threading.Condition()
        self.otherAddress = (otherAddress,dst_port)
        self.src_port = src_port
        self.dst_port = dst_port

        ##constructor, needs max window size for requirements and state for bidir
        ##should also initialize buffers etc
        self.currentWindowSize = 1

        self.seq = 0
        self.ack = 0

        ### Threading Queues:

        self.dgram_queue_in = Queue.Queue() # contains EVILPacket objs
        # self.dgram_queue_out = queue.Queue() # contains EVILPacket objs
        self.dgram_unconf = []
        self.dgram_unsent = []
        self.str_queue_in = Queue.Queue()
        self.str_queue_out = Queue.Queue()

        self.queue_cond = threading.Condition()
        self.socket = socket

        self.establishedCondition = threading.Condition()
        self.resendTimer = 0
        self.thread = threading.Thread(None, self.c_thread, "c_thread")
        self.thread.start()

    def setState(self, newState, timerReset=True):
        self.stateCond.acquire()
        self.state = newState
        if timerReset:
            self.resendTimer = 0
        self.stateCond.release()

    def setMaxWindowSize(self, W):
        self.max_window_size = W

    ##called by the socket on each connection passing in a packet that was
    ##sent to the connection, could be an ack or data, checksum has been done
    def handleIncoming(self,packet):
        try:
            self.dgram_queue_in.put(packet,timeout=0.5)
            debugLog("added incoming packet to queue")
            self.queue_cond.acquire()
            self.queue_cond.notifyAll()
            debugLog("queue notification sent")
            self.queue_cond.release()
            self.queue_cond.release()
            debugLog("released twice")
        except Exception as e:
            pass


    ##called by the application when it wants to read the data from the stream
    ##pauses until data is available, deletes data from the buffer once gotten
    def get(self,maxSize,block=True,timeout=None):
        if self.state != STATE.ESTABLISHED and self.str_queue_out.empty():
            raise Exception("Cannot read from non-established connection")
        return self.str_queue_in.get(block,timeout)


    ##called by the application when it wants to send data to the connection
    ##should add the data to the output buffer, then handle it when appropriate
    def send(self,data,block=True,timeout=None):
        if self.state != STATE.ESTABLISHED:
            raise Exception("Cannot write to non-established connection")
        dataChunks = []
        while len(data) != 0:
            dataChunks.append(data[:MAX_SEND_BYTES])
            data = data[MAX_SEND_BYTES:]

        for i in range(len(dataChunks)):
            self.str_queue_out.put(dataChunks[i],block,timeout)
        self.queue_cond.acquire()
        self.queue_cond.notify()
        self.queue_cond.release()



    ##send a FIN, set state appropriately
    def close(self):
        debugLog("connection.close() called!")
        if self.state == STATE.CLOSED:
            raise Exception("Cannot close an already-closed connection")
        dgram = self.new_dgram()
        dgram.setFlag(util.FLAG.FIN,True)
        for _ in range(10):
            self.socket.addToOutput(self.otherAddress,dgram)
        self.stateCond.acquire()
        self.state = STATE.CLOSED
        self.stateCond.notifyAll()
        self.stateCond.release()


    def new_dgram(self,seq=None,ack=None):
        if seq == None:
            seq = self.seq
        if ack == None:
            ack = self.ack
        dgram = util.EVILPacket()
        dgram.src_port = self.src_port
        dgram.dst_port = self.dst_port
        dgram.seq = seq
        dgram.ack = ack
        dgram.window = self.max_window_size

        return dgram

    def process_data_str(self,data):
        # seq will be added in EVIL.py
        dgram = self.new_dgram()
        dgram.data = data
        dgram.seq = self.seq + len(data)
        dgram.window = self.max_window_size
        dgram.checksum = dgram.generateCheckSum()

        self.seq += len(data) #TODO  may change

        if len(self.dgram_unconf) >= self.max_send_size:
            debugLog("queue full; deferring packet")
            self.dgram_unsent.append(dgram)
        else:
            debugLog("appended packet to queue")
            self.dgram_unconf.append(dgram)
            self.socket.addToOutput(self.otherAddress,dgram)

    def process_dgram(self,dgram):
        self.stateCond.acquire()
        oldState = self.state
        self.max_send_size = dgram.window
        new_dgram = self.new_dgram()
        if dgram.checkFlag(util.FLAG.FIN):
            debugLog("FIN received. Closing connection.")
            self.state = STATE.CLOSED
            self.stateCond.notifyAll()
        elif oldState != STATE.ESTABLISHED:
            if oldState == STATE.CLOSED:
                pass
            if oldState == STATE.SYN_SENT:
                if dgram.checkFlag(util.FLAG.SYN) and dgram.checkFlag(util.FLAG.ACK):
                    new_dgram.setFlag(util.FLAG.ACK,True)
                    self.setState(STATE.ESTABLISHED)
                    self.stateCond.notifyAll()
                    self.socket.addToOutput(self.otherAddress,new_dgram)
                    debugLog("Sent ACK")
            if oldState == STATE.SYN_RECV:
                if dgram.checkFlag(util.FLAG.ACK):
                    self.setState(STATE.ESTABLISHED)
                    self.stateCond.notifyAll()
                    debugLog("Connection Established")
            if oldState == STATE.FIN_WAIT_1:
                pass
            if oldState == STATE.FIN_WAIT_2:
                pass
            if oldState == STATE.FIN_CLOSING:
                pass
            if oldState == STATE.TIME_WAIT:
                pass
            if oldState == STATE.CLOSE_WAIT:
                pass
            if oldState == STATE.LAST_ACK:
                pass
            pass
        else:
            if dgram.checkFlag(util.FLAG.SYN) and dgram.checkFlag(util.FLAG.ACK):
                new_dgram.setFlag(util.FLAG.ACK,True)
                debugLog("Resending ACK")
                self.socket.addToOutput(self.otherAddress,new_dgram)
            dataLen = len(dgram.data)
            if self.ack + dataLen < dgram.seq:
                #Out of order packet. Will be dropped.
                # Re-acknowledge last received in-order packet with RET set
                new_dgram.setFlag(util.FLAG.RET,True)
                self.socket.addToOutput(self.otherAddress,new_dgram)
                debugLog("Received packet out-of-order. Re-ACKing last received packet")
                return

            self.ack += len(dgram.data) #TODO: need to change to fit data type
            rcvd_ack = dgram.ack
            j = len(self.dgram_unconf)
            i = 0
            while i < j:
                if self.dgram_unconf[i].seq <= rcvd_ack:
                    self.dgram_unconf.pop(i)
                    i -= 1
                    j -= 1
                i += 1
            if len(dgram.data) != 0:
                self.str_queue_in.put(dgram.data)
                new_dgram = self.new_dgram() #get new ack number
                debugLog("ACKing received packet")
                self.socket.addToOutput(self.otherAddress,new_dgram)
            elif dgram.checkFlag(util.FLAG.RET):
                debugLog("Got RET - resending!")
                #need to resend unconfirmed packets.
                #will fake resendTimer so that resend happens right away
                self.resendTimer = time.time() - (self.DEFAULT_TIMEOUT + 1)
        self.stateCond.release()

    def checkTimeout(self):
        if (time.time() - self.resendTimer) < self.DEFAULT_TIMEOUT:
            return
        new_dgram = self.new_dgram()
        self.stateCond.acquire()
        oldState = self.state

        if oldState == STATE.SYN_RECV:
            new_dgram.setFlag(util.FLAG.SYN,True)
            new_dgram.setFlag(util.FLAG.ACK,True)
            self.socket.addToOutput(self.otherAddress,new_dgram)
            debugLog("resent SYN+ACK")
        elif oldState == STATE.SYN_SENT:
            new_dgram.setFlag(util.FLAG.SYN,True)
            self.socket.addToOutput(self.otherAddress,new_dgram)
            debugLog("resent SYN")
        elif oldState == STATE.ESTABLISHED:
            #Need to resend any unACK-ed data
            for dgram in self.dgram_unconf:
                debugLog("Resending data")
                self.socket.addToOutput(self.otherAddress,dgram)

        self.resendTimer = time.time()
        self.stateCond.release()

    def establishConnection(self):
        self.stateCond.acquire()
        debugLog(str(self.state))
        new_dgram = self.new_dgram()
        new_dgram.setFlag(util.FLAG.SYN,True)
        if self.state == STATE.SYN_RECV:
            new_dgram.setFlag(util.FLAG.ACK,True)
            debugLog("Sending SYN+ACK")
        else:
            debugLog("Sending SYN")
        self.socket.addToOutput(self.otherAddress,new_dgram)
        while self.state != STATE.ESTABLISHED and self.state != STATE.CLOSED:
            self.stateCond.wait()
        debugLog(str(self.state))
        self.stateCond.release()
        return


    # Waits for input, calls appropriate fn
    def c_thread(self):

        self.resendTimer = time.time()
        while True:
            cond = self.queue_cond
            cond.acquire()
            if self.dgram_queue_in.empty() and self.str_queue_out.empty():
                ##debugLog("waiting")
                cond.wait(timeout=1)
                ##debugLog("wait interrupted")
            cond.release()
            while not self.dgram_queue_in.empty():
                dgram = self.dgram_queue_in.get()
                debugLog("Got incoming packet from queue")
                self.process_dgram(dgram)
            while len(self.dgram_unconf) < self.max_send_size and len(self.dgram_unsent) > 0:
                dgram = self.dgram_unsent.pop(0)
                dgram.ack = self.ack
                debugLog("Sending delayed data")
                self.socket.addToOutput(self.otherAddress,dgram)
                self.dgram_unconf.append(dgram)
            while not self.str_queue_out.empty():
                held = len(self.dgram_unconf)
                debugLog("Got incoming data from queue")
                data = self.str_queue_out.get()
                self.process_data_str(data)
            if self.state == STATE.CLOSED:
                debugLog("Connection closed")
                break
            self.checkTimeout()
        #TODO: call socket fn to remove conn from list
