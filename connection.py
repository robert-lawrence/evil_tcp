##Connection for EVIL protocol

##Connection is created and held by a socket, and held by ONE application

##Connection is responsible for maintaining the sliding window ARQ and its
##in/out buffers, as well as its own state, including termination

##when a connection is first created it is either in:
##              syn_recv (if it was created with socket.accept)
##              syn_sent (if it was created with socket.connect)

import queue
import threading
from util import EVILPacket
from util import debugLog
import util
import time

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
        self.otherAddress = otherAddress
        self.src_port = src_port
        self.dst_port = dst_port

        ##constructor, needs max window size for requirements and state for bidir
        ##should also initialize buffers etc
        self.otherAddress = ("not initialized", 0)
        self.currentWindowSize = 1
        self.state = STATE.CLOSED

        self.seq = 0
        self.ack = 0

        ### Threading Queues:

        self.dgram_queue_in = queue.Queue() # contains EVILPacket objs
        # self.dgram_queue_out = queue.Queue() # contains EVILPacket objs
        self.dgram_unconf = []
        self.dgram_unsent = []
        self.str_queue_in = queue.Queue()
        self.str_queue_out = queue.Queue()

        self.queue_cond = threading.Condition()
        self.socket = socket

        self.establishedCondition = threading.Condition()
        self.resendTimer = 0

    def setState(self, newState, timerReset=True)
        self.stateCond.acquire()
        self.state = newState
        if timerReset:
            self.resendTimer = 0
        self.stateCond.release()


    ##called by the socket on each connection passing in a packet that was
    ##sent to the connection, could be an ack or data, checksum has been done
    def handleIncoming(packet):
        try:
            self.dgram_queue_in.put(packet,timeout=0.5)
            self.queue_cond.acquire()
            self.queue_cond.notify()
            self.queue_cond.release()
        except Exception as e:
            pass


    ##called by the application when it wants to read the data from the stream
    ##pauses until data is available, deletes data from the buffer once gotten
    def get(maxSize,block=True,timeout=None):
        if self.state != STATE.ESTABLISHED and self.str_queue_out.empty():
            throw Exception("Cannot read from non-established connection")
        return self.str_queue_out.get(block,timeout)


    ##called by the application when it wants to send data to the connection
    ##should add the data to the output buffer, then handle it when appropriate
    def send(data,block=True,timeout=None):
        if self.state != STATE.ESTABLISHED:
            throw Exception("Cannot write to non-established connection")
        self.str_queue_in.put(data,block,timeout)
        self.queue_cond.acquire()
        self.queue_cond.notify()
        self.queue_cond.release()

    ##send a FIN, set state appropriately
    def close():
        pass


    def new_dgram(seq=None,ack=None):
        if seq == None:
            seq = self.seq
        if ack == None:
            ack = self.ack
        dgram = util.EVILPacket()
        dgram.src_port = self.my_port
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
        dgram.window = self.currentWindowSize
        dgram.checksum = drgram.generateCheckSum()

        self.seq += len(data) #TODO  may change

        if len(self.dgram_unconf) >= self.max_send_size:
            self.dgram_unsent.append(dgram)
        else:
            self.dgram_unconf.append(dgram)
            socket.addToOutput(self.otherAddress,dgram)

    def process_dgram(self,dgram):
        self.stateCond.acquire()
        oldState = self.state
        self.max_send_size = dgram.window
        new_dgram = self.new_dgram()
        if oldState != STATE.ESTABLISHED:
            if oldState == STATE.CLOSED:
                pass
            if oldState == STATE.LISTEN:
                if dgram.checkFlag(util.FLAG.SYN):
                    new_dgram.setFlag(util.FLAG.SYN,True)
                    new_dgram.setFlag(util.FLAG.ACK,True)
                    setState(STATE.SYN_RECV)
                    self.stateCond.notifyAll()
                    socket.addToOutput(self.otherAddress,new_dgram)
                    debugLog("Sent SYN+ACK")
            if oldState == STATE.SYN_RECV:
                if dgram.checkFlag(util.FLAG.ACK):
                    setState(STATE.ESTABLISHED)
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
            #TODO !!!
            pass
        else:
            dataLen = len(dgram.data)
            if self.ack + dataLen != dgram.seq:
                #Out of order packet. Will be dropped.
                # Re-acknowledge last received in-order packet
                socket.addToOutput(self.otherAddress,new_dgram)
                debugLog("Received packet out-of-order. Re-ACKing last received packet")
                return

            self.ack += len(dgram.data) #TODO: need to change to fit data type
            rcvd_ack = dgram.ack
            j = len(self.dgram_unconf)
            i = 0
            while i < j:
                if self.dgram_unconf[i].ack < rcvd_ack:
                    self.dgram_unconf.pop(i)
                    i -= 1
                    j -= 1
                i += 1
            if len(dgram.data) != 0:
                self.str_queue_in.put(dgram.data)
            new_dgram = self.new_dgram() #get new ack number
            debugLog("ACKing received packet")
            socket.addToOutput(self.otherAddress,new_dgram)
        self.stateCond.release()

    def checkTimeout(self):
        if time.clock() - self.resendTimer < DEFAULT_TIMEOUT:
            return
        new_dgram = self.new_dgram()
        self.stateCond.acquire()
        oldState = self.state

        if oldState == STATE.SYN_RECV:
            new_dgram.setFlag(util.FLAG.SYN,True)
            new_dgram.setFlag(util.FLAG.ACK,True)
            socket.addToOutput(self.otherAddress,new_dgram)
            debugLog("sent SYN+ACK")
        elif oldState == STATE.SYN_SENT:
            newdgram.setFlag(util.FLAG.SYN,True)
            sent(new_dgram)
            debugLog("sent SYN")
        elif currState == STATE.ESTABLISHED:
            #Need to resend any unACK-ed data
            for dgram in self.dgram_unconf:
                debugLog("Resending data")
                socket.addToOutput(self.otherAddress,dgram)

        self.resendTimer = 0
        self.sateCond.release()



    # Waits for input, calls appropriate fn
    def c_thread():

        self.resendTimer = time.clock()
        while True:
            cond = self.queue_cond
            cond.acquire()
            if self.dgram_queue_in.empty() and self.str_queue_out.empty():
                cond.wait()
            cond.release()
            while not self.dgram_queue_in.empty():
                dgram = self.dgram_queue_in.get()
                process_dgram(dgram)
            while len(self.dgram_unconf) < self.max_send_size and len(self.dgram_unsent) > 0:
                dgram = self.dgram_unsent.pop(0)
                dgram.ack = self.ack
                debugLog("Sending delayed data")
                sent(dgram)
                self.dgram_unconf.append(dgram)
            while not self.str_queue_out.empty():
                held = len(self.dgram_unconf)
                data = self.str_queue_out.get()
                process_data_str(data)
            if not check_connection():
                break
