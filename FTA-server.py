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
            sessionThread = threading.Thread(None, self.handleSession, "session_thread", (newSessionConnection,))
            sessionThread.start()

    def handleSession(self, conn):
        debugLog("new session started with " + conn.otherAddress[0] + ":" + str(conn.otherAddress[1]))
        self.sessionState = SESSIONSTATE.IDLE
        self.filename = ""
        while True:
            string = conn.get(1024)
            debugLog("received " + string + " from " + conn.otherAddress[0] + ":" + str(conn.otherAddress[1]))

            if self.sessionState == SESSIONSTATE.IDLE:
                if string == "get":
                    self.sessionState = SESSIONSTATE.GET_1
                    debugLog("Session now get 1")
                    conn.send("get")
                elif string == "post":
                    self.sessionState = SESSIONSTATE.POST_1
                    debugLog("Session now post 1")
                    conn.send("post")
            elif self.sessionState == SESSIONSTATE.GET_1:
                self.filename = string
                if os.path.isfile(self.filename):
                    self.sessionState = SESSIONSTATE.GET_2
                    debugLog("Session now get 2")
                    f = open(self.filename,'r')
                    fileLen = len(f.read())
                    conn.send("got it: "+str(fileLen))
                    f.close()
                else:
                    self.sessionState == SESSIONSTATE.IDLE
                    debugLog("Session now idle")
                    conn.send("back to idle")
            elif self.sessionState == SESSIONSTATE.GET_2:
                if string == "send file":
                    f = open(self.filename, 'r')
                    conn.send(f.read())
                    f.close()
                    conn.send("back to idle")
                else:
                    self.sessionState == SESSIONSTATE.IDLE
                    debugLog("Session now idle")
                    conn.send("back to idle")
            elif self.sessionState == SESSIONSTATE.POST_1:
                self.filename = string
                self.sessionState = SESSIONSTATE.POST_2
                debugLog("Session now post 2")
                conn.send("send file")
            elif self.sessionState == SESSIONSTATE.POST_2:
                    f = open(self.filename, 'w')
                    f.write(string)
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
