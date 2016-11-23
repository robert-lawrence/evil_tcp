


###Outline for socket.py

import socket
import threading
import queue

class Evil:
    BUFSIZE = 1000
    DEFAULTMAXWIN = 1

    def __init__(self):

        self.connections = []
        self.connectionsLock = threading.Lock()
        self.unknownPackets = queue.Queue()

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.port = 0
        self.host = 0

    def main(self):
        debugLog("mainThread started on port " + PORT)

        while True:
            msg, address = sock.recvfrom(Evil.BUFSIZE)
            if address in connections:
                connectionsLock.acquire()
                connections[(address, CONN)].handleIncoming(msg)
                connectionsLock.release()
            else:
                unknownPackets.put((msg, address), False)

    def bind(self, host, port):
        sock.bind(self.host, self.port)
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
        newConn = Connection(Evil.DEFAULTMAXWIN, STATE.SYN_RECV, unknownPacket[1])
        self.connections[(address, CONN)] = newConn
        self.connectionsLock.release()

        return newConn



    def connect(self, host, port):
        """
        Called by client code - socket and connection threads should not touch!
        blocks while attempting to establish a connection with specified server

        Return: a Connection instance (if successful) or an error
        Errors: if socket closed, throw exception
        """
        connectionsLock.acquire()
        newConn = connection(Evil.DEFAULTMAXWIN, STATE.SYN_RECV, (host, port))
        connections[(address, CONN)] = newConn
        connectionsLock.release()
        debugLog("new connection created with: " + host + " on port " + str(port))
