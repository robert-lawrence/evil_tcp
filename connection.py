##Connection for EVIL protocol

##Connection is created and held by a socket, and held by ONE application

##Connection is responsible for maintaining the sliding window ARQ and its
##in/out buffers, as well as its own state, including termination

##when a connection is first created it is either in:
##              syn_recv (if it was created with socket.accept)
##              syn_sent (if it was created with socket.connect)

from enum import Enum
import queue
import threading
from util import EVILPacket

class STATE(Enum):
    CLOSED = 1,
    LISTEN = CLOSED << 1,
    SYN_RECV = LISTEN << 1,
    SYN_SENT = SYN_RECV << 1,
    ESTABLISHED = SYN_SENT << 1,
    FIN_WAIT_1 = ESTABLISHED << 1,
    FIN_WAIT_2 = FIN_WAIT_1 << 1,
    FIN_CLOSING = FIN_WAIT_2 << 1,
    TIME_WAIT = FIN_CLOSING << 1,
    CLOSE_WAIT = TIME_WAIT << 1,
    LAST_ACK = CLOSE_WAIT << 1,
    CLOSED = LAST_ACK << 1


class Connection:

    ##member variables are window size, max window size, in/out buffers, and
    ##a state enum


    def __init__(self, src_port, dst_port, maxWindowSize, state, otherAddress):
        self.max_window_size = maxWindowSize
        self.state = state
        self.otherAddress = otherAddress
        self.src_port = src_port
        self.dst_port = dst_port

        ##constructor, needs max window size for requirements and state for bidir
        ##should also initialize buffers etc
        self.otherAddress = ("not initialized", 0)
        self.maxWindowSize = 1
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
        dgram = EVILPacket()
        dgram.src_port = self.my_port
        dgram.dst_port = self.dst_port
        dgram.seq = seq
        dgram.ack = ack

    def process_data_str(self,data):
        # seq will be added in EVIL.py
        dgram = self.new_dgram()
        dgram.data = data
        #TODO: do we need to set FLAGS?
        self.dgram_unconf.append(dgram)
        #TODO: call method in EVIL to send dgram

    def process_dgram(self,dgram):
        if self.state != STATE.ESTABLISHED:
            #TODO !!!
            pass
        else:
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


    ##thread that handles the output buffer, adding its requests to the socket
    ##when the sliding window allows
    def outputManager():

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


