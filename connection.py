##Connection for EVIL protocol

##Connection is created and held by a socket, and held by ONE application

##Connection is responsible for maintaining the sliding window ARQ and its
##in/out buffers, as well as its own state, including termination

##when a connection is first created it is either in:
##              syn_recv (if it was created with socket.accept)
##              syn_sent (if it was created with socket.connect)

from enum import Enum
import queue

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

    ##constructor, needs max window size for requirements and state for bidir
    ##should also initialize buffers etc
    otherAddress = ("not initialized", 0)
    maxWindowSize = 1
    state = STATE.CLOSED

    seq = 0
    ack = 0

    ### Threading Queues:

    dgram_queue_in = queue.Queue()
    dgram_queue_out = queue.Queue()
    str_queue_in = queue.Queue()
    str_queue_out = queue.Queue()

    def __init__(self, my_port, their_port, maxWindowSize, state, otherAddress):
        self.maxWindowSize = maxWindowSize
        self.state = state
        self.otherAddress = otherAddress
        self.my_port = my_port
        self.their_port = their_port



    ##called by the socket on each connection passing in a packet that was
    ##sent to the connection, could be an ack or data, checksum has been done
    def handleIncoming(packet):
        try:
            self.dgram_queue_in.put(packet,timeout=0.5)
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

    ##send a FIN, set state appropriately
    def close():


    ##thread that handles the output buffer, adding its requests to the socket
    ##when the sliding window allows
    def outputManager():
