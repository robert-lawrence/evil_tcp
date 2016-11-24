import sys
import getopt
import EVIL
import threading
from util import debugLog

global _debug

class FTAclient:

    def __init__(self, argv):
        self.serverAddress = "127.0.0.1"
        self.serverPort = 1337
        self.maxMessageSize = 1024
        self.connected = False
        global _debug

        try:
            opts, args = getopt.getopt(argv, "a:p:d")
        except getopt.GetoptError:
            usage()
            sys.exit(2)

        for opt, arg in opts:
                if opt == '-a':
                    self.serverAddress = arg
                elif opt == '-p':
                    self.serverPort = arg
                elif opt == '-d':
                    _debug = True
                    debugLog("Maximum Verbosity!")

        self.sock = EVIL.Evil()
        self.sock.bind(('', 0)) ##tells os to bind to all hostnames on this machine with a chosen available port
        debugLog("socket bound to: " + sock.getsockname()[0] + ":" + str(sock.getsockname()[1]))



    def connect(self):
        self.connection = self.sock.connect(serverAddress, serverPort)
        self.connected = True
        debugLog("created connection with " + newSession.otherAddress[0] + ":" + str(newSession.otherAddress[1]))

    def get(self, F):
        if self.connected:
            self.connection.send(F)
            print(self.connection.get(1024))
        else:
            raise UnboundLocalError('Client has no connection to a server, cannot fetch')

    def window(self, W):
        self.sock.setMaxWindowSize(W)

    def terminate(self):
        self.sock.close()
        sys.exit()

def main(argv):
    return FTAclient(argv)

def test(argv):
    app = main(argv)
    app.connect()
    app.get("Hello, World")

test(sys.argv)
##main(sys.argv)
