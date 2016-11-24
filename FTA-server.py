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
        sessionState = SESSIONSTATE.IDLE
        filename = ""
        fileSize = 0
        while True:
            string = conn.get(1024)
            debugLog("received " + string + " from " + conn.otherAddress[0] + ":" + str(conn.otherAddress[1]))

            if sessionState == SESSIONSTATE.IDLE:
                if string == "get":
                    sessionState = SESSIONSTATE.GET_1
                    debugLog("Session now get 1")
                    conn.send("get")
                elif string[0:6] == "post: ":
                    fileSize = int(string[6:])
                    sessionState = SESSIONSTATE.POST_1
                    debugLog("Session now post 1")
                    conn.send("post")
            elif sessionState == SESSIONSTATE.GET_1:
                filename = string
                if os.path.isfile(filename):
                    sessionState = SESSIONSTATE.GET_2
                    debugLog("Session now get 2")
                    f = open(filename,'r')
                    fileLen = len(f.read())
                    conn.send("got it: " + str(fileLen))
                    f.close()
                else:
                    sessionState == SESSIONSTATE.IDLE
                    debugLog("Session now idle")
                    conn.send("back to idle")
            elif sessionState == SESSIONSTATE.GET_2:
                if string == "send file":
                    f = open(filename, 'r')
                    conn.send(f.read())
                    f.close()
                    conn.send("back to idle")
                else:
                    sessionState == SESSIONSTATE.IDLE
                    debugLog("Session now idle")
                    conn.send("back to idle")
            elif sessionState == SESSIONSTATE.POST_1:
                filename = string
                sessionState = SESSIONSTATE.POST_2
                debugLog("Session now post 2")
                conn.send("send file")
            elif sessionState == SESSIONSTATE.POST_2:
                    while len(string) < fileSize:
                        string += conn.get(1024)
                    f = open(filename, 'w')
                    f.write(string)
                    f.close()
                    debugLog("Post Complete")
                    sessionState = SESSIONSTATE.IDLE
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
        debugLog("Server Closed")
        sys.exit()

def main(argv):
    return FTAserver(argv)

def test(argv):
    app = main(argv)

test(sys.argv[1:])
##main(sys.argv)
