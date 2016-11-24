import sys
import getopt
import EVIL
import threading
from util import debugLog

global _debug

class FTAserver:

    def operate(self):
        while True:
            debugLog("server accepting connections...")
            newSessionConnection = self.sock.accept()
            debugLog("accepted connection from " + newSessionConnection.otherAddress[0] + ":" + str(newSessionConnection.otherAddress[1]))
            sessionThread = threading.Thread(None, handleSession, newSessionConnection, "session_thread")
            sessionThread.start()

    def handleSession(self, conn):
        debugLog("new session started with " + conn.otherAddress[0] + ":" + str(conn.otherAddress[1]))
        while True:
            string = conn.get(maxMessageSize)
            debugLog("received " + string.data + " from " + conn.otherAddress[0] + ":" + str(conn.otherAddress[1]))
            reply = string.data.upper()
            debugLog("replying to " + conn.otherAddress[0] + ":" + str(conn.otherAddress[1]) + " with: " + reply)
            conn.send(reply)

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
