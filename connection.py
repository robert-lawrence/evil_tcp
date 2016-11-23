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

class STATE():
    CLOSED = 2
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
    DEFAULT_TIMEOUT = 1000

    def __init__(self, src_port, dst_port, maxWindowSize, state, otherAddress, socket):
        self.max_window_size = maxWindowSize
        self.state = state
        self.stateCond = threading.Condition()
        self.otherAddress = otherAddress
        self.src_port = src_port
        self.dst_port = dst_port

        ##constructor, needs max window size for requirements and state for bidir
        ##should also initialize buffers etc
        self.otherAddress = ("not initialized", 0)
        self.maxWindowSize = 1
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

        return dgram

    def process_data_str(self,data):
        # seq will be added in EVIL.py
        dgram = self.new_dgram()
        dgram.data = data
        dgram.seq = self.seq + len(data)
        dgram.window = self.currentWindowSize
        dgram.checksum = drgram.generateCheckSum()

        self.seq += len(data) #TODO  may change

        self.dgram_unconf.append(dgram)

        socket.addToOutput(dgram)

    def process_dgram(self,dgram):
        self.sateCond.acquire()
        state = self.STATE
        new_dgram = self.new_dgram()
        if state != STATE.ESTABLISHED:
            if state == STATE.CLOSED:
                pass
            if state == STATE.LISTEN:
                if dgram.checkFlag(util.FLAG.SYN):
                    new_dgram.setFlag(util.FLAG.SYN,True)
                    new_dgram.setFlag(util.FLAG.ACK,True)
                    self.STATE = STATE.SYN_RECV
                    self.resendTimer = 0
            if state == STATE.SYN_RECV:
                if dgram.checkFlag(util.FLAG.ACK):
                    self.STATE = STATE.ESTABLISHED
                    self.resendTimer = 0
            if state == STATE.FIN_WAIT_1:
            if state == STATE.FIN_WAIT_2:
            if state == STATE.FIN_CLOSING:
            if state == STATE.TIME_WAIT:
            if state == STATE.CLOSE_WAIT:
            if state == STATE.LAST_ACK:
            #TODO !!!
            pass
        else:
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
        self.stateCond.release()

    def establishConnection(self):

        while True:
            if (resendTimer % DEFAULT_TIMEOUT == 0):
                stateCond.acquire()
                currState = state
                stateCond.release()

                if currState == STATE.ESTABLISHED
                    debugLog("Connection established")
                    return True
                elif currState == STATE.SYN_RECV
                    reply = new_dgram()
                    reply.setFlag(FLAGS.SYN, True)
                    reply.setFlag(FLAGS.ACK, True)
                    debugLog("Sent SYN+ACK")
                    send(reply)
                elif currState == STATE.SYN_SENT
                    reply = new_dgram()
                    reply.setFlag(FLAGS.SYN, True)
                    debugLog("Sent SYN")
                    send(reply)

            self.resendTimer += 1

    # Waits for input, calls appropriate fn
    def c_thread():

        while True:
            cond = self.queue_cond
            cond.acquire()
            if self.dgram_queue_in.empty() and self.str_queue_out.empty():
                cond.wait()
            cond.release()
            while not self.dgram_queue_in.empty():
                dgram = self.dgram_queue_in.get()
                process_dgram(dgram)
            while not self.str_queue_out.empty():
                held = len(self.dgram_unconf)
                data = self.str_queue_out.get()
                if held >= self.max_window_size:
                    self.dgram_unsent.append(data)
                else:
                    process_data_str(data)
            if not check_connection():
                break
