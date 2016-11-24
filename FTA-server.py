import sys
import getopt
import EVIL
import threading
from util import debugLog
import os.path

global _debug

class SESSIONSTATE():
    IDLE = 1
    GET_1 = 2
    GET_2 = 3
    POST_1 = 5
    POST_2 = 6
    POST_3 = 7

class FTAserver():

    def operate(self):
        while True:
            debugLog("server accepting connections...")
            newSessionConnection = self.sock.accept()
            debugLog("accepted connection from " + newSessionConnection.otherAddress[0] + ":" + str(newSessionConnection.otherAddress[1]))
<<<<<<< HEAD
            sessionThread = threading.Thread(None, handleSession, "session_thread",  newSessionConnection)
=======
            sessionThread = threading.Thread(None, self.handleSession, "session_thread", (newSessionConnection,))
>>>>>>> origin/master
            sessionThread.start()

    def handleSession(self, conn):
        debugLog("new session started with " + conn.otherAddress[0] + ":" + str(conn.otherAddress[1]))
        self.sessionState = SESSIONSTATE.IDLE
        self.filename = ""
        while True:
            string = conn.get(maxMessageSize)
            debugLog("received " + string.data + " from " + conn.otherAddress[0] + ":" + str(conn.otherAddress[1]))

            if self.sessionState == SESSIONSTATE.IDLE:
                if string.data == "get":
                    self.sessionState = SESSIONSTATE.GET_1
                    debugLog("Session now get 1")
                    self.connection.send("get")
                elif string.data == "post":
                    self.sessionState == SESSIONSTATE.POST_1
                    debugLog("Session now post 1")
                    self.connection.send("post")
            elif self.sessionState == SESSIONSTATE.GET_1
                self.filename = string.data
                if os.path.isfile(filename):
                    self.sessionState == SESSIONSTATE.GET_2
                    debugLog("Session now get 2")
                    self.connection.send("got it")
                else:
                    self.sessionState == SESSIONSTATE.IDLE
                    debugLog("Session now idle")
                    self.connection.send("back to idle")
            elif self.sessionState == SESSIONSTATE.GET_2
                if string.data == "send file":
                    f = open(filename, 'r')
                    self.connection.send(f.read())
                    f.close()
                    self.connection.send("back to idle")
                else:
                    self.sessionState == SESSIONSTATE.IDLE
                    debugLog("Session now idle")
                    self.connection.send("back to idle")
            elif self.sessionState == SESSIONSTATE.POST_1
                self.filename = string.data
                self.sessionState == SESSIONSTATE.POST_2
                debugLog("Session now post 2")
                self.connection.send("send file")
            elif self.sessionState == SESSIONSTATE.POST_2
                    f = open(filename, 'w')
                    f.write(data.string)
                    f.close()
                    debugLog("Post Complete")
                    self.sessionState = SESSIONSTATE.IDLE
                    debugLog("Session now idle")


    def __init__(self, argv):
        self.ourPort = 404
        self.maxMessageSize = 1024

        try:
            opts, args = getopt.getopt(argv, "x:d")
        except getopt.GetoptError:
            usage()
            sys.exit(2)

        for opt, arg in opts:
                if opt == '-x':
                    self.ourPort = int(arg)
                elif opt == '-d':
                    _debug = True
                    debugLog("Maximum Verbosity!")

        self.sock = EVIL.Evil()
        self.sock.bind('', self.ourPort)
        debugLog("socket bound to: " + self.sock.sock.getsockname()[0] + ":" + str(self.ourPort))

        operateThread = threading.Thread(None, self.operate)
        operateThread.start()

    def window(self, W):
        self.sock.setMaxWindowSize(W)

    def terminate(self):
        self.sock.close()
        sys.exit()

def main(argv):
    return FTAserver(argv)

def test(argv):
    app = main(argv)

test(sys.argv[1:])
##main(sys.argv)
