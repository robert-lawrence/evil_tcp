


###Outline for socket.py

import socket
import dummy_threading

class Evil:
    BUFSIZE = 1000
    PORT = 0
    HOST = 0
    MAXWIN = 1
    connections = []
    connectionsLock = threading.lock()
    unknownPackets = queue.Queue()

    def __init__(self, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        PORT = port
        HOST = host
        sock.bind(HOST, PORT)
        mainThread = threading.Thread(None, main, mainThread)
        mainThread.start()

    def accept(self):
        """
        called by client code - Socket and connection threads should not touch!
        blocks until a new connection is received and a Connection object has
        been created.

        Return: a Connection instance
        Errors: if socket closed, throw exception
        """
        unknownPacket = unknownPackets.get()

        connectionsLock.acquire()
        newConn = connection(MAXWIN, STATE.SYN_RECV, unknownPacket[1]])
        connections[(address, CONN)] = newConn
        connectionsLock.release()

        return newConn



    def connect(self, host, port):
        """
        Called by client code - socket and connection threads should not touch!
        blocks while attempting to establish a connection with specified server

        Return: a Connection instance (if successful) or an error
        Errors: if socket closed, throw exception
        """
        connectionsLock.acquire()
        newConn = connection(MAXWIN, STATE.SYN_RECV, (host, port))
        connections[(address, CONN)] = newConn
        connectionsLock.release()
        pass


    def main(self):
        print "mainThread started on port " + PORT

        while True:
            msg, address = sock.recvfrom(BUFSIZE)
            if address in connections:
                connectionsLock.acquire()
                connections[(address, CONN)].handleIncoming(msg)
                connectionsLock.release()
            else:
                unknownPackets.put((msg, address), False)
        pass
