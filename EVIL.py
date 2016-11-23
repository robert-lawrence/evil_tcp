


###Outline for socket.py

import socket
import threading
import queue

import connection
import util
from util import debugLog

class Evil:
    BUFSIZE = 1000
    DEFAULTMAXWIN = 1

    def __init__(self):

        self.connections = []
        self.connectionsLock = threading.Lock()
        self.unknownPackets = queue.Queue()

        self.outgoingPackets = queue.Queue()

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def listener(self):
        debugLog("listenerThread started on port " + PORT)

        while True:
            msg, address = self.sock.recvfrom(Evil.BUFSIZE)
            packet = EVILPacket()
            packet = packet.parseFromString(msg)
            if address in connections:
                self.connectionsLock.acquire()
                self.connections[(address, CONN)].handleIncoming(packet)
                self.connectionsLock.release()
            else:
                if packet.checkFlag(FLAGS.SYN):
                    self.unknownPackets.put((packet, address), False)

    def speaker(self):
        debugLog("speakerThread started on port " + PORT)

        while True:
            recipient, packet = self.outgoingPackets.get()
            self.sock.sendto(packet.toString(), recipient)



    def bind(self, host, port):
        self.sock.bind(host, port)
        listenerThread = threading.Thread(None, listener, listenerThread)
        listenerThread.start()
        speakerThread = threading.Thread(None, speaker, speakerThread)
        speakerThread.start()

    def accept(self):
        """
        called by client code - Socket and connection threads should not touch!
        blocks until a new connection is received and a Connection object has
        been created.

        Return: a Connection instance
        Errors: if socket closed, throw exception
        """
        unknownPacket = unknownPackets.get()

        self.connectionsLock.acquire()
        newConn = Connection(self.port, unknownPacket[0], Evil.DEFAULTMAXWIN, STATE.SYN_RECV, unknownPacket[1], self)
        self.connections[((unknownPacket[0], unknownPacket[1]), CONN)] = newConn
        self.connectionsLock.release()

        newConn.establishConnection()

        newConn.establishedCondition.acquire()
        newConn.establishedCondition.wait()
        newConn.establishedCondition.release()
        return newConn



    def connect(self, host, port):
        """
        Called by client code - socket and connection threads should not touch!
        blocks while attempting to establish a connection with specified server

        Return: a Connection instance (if successful) or an error
        Errors: if socket closed, throw exception
        """
        self.connectionsLock.acquire()
        newConn = Connection(self.port, port, Evil.DEFAULTMAXWIN, STATE.SYN_SENT, host, self)
        self.connections[((host, port), CONN)] = newConn
        self.connectionsLock.release()
        newConn.establishConnection()
        debugLog("new connection created with: " + host + " on port " + str(port))
        return newConn

    def addToOutput(self, address, packet):
        self.outgoingPackets.put((address, packet))

    def close(self):
        for connection in self.connections:
            connection.close()
