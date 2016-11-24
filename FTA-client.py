import sys
import getopt
import EVIL
import threading
from util import debugLog
import os.path

global _debug

MAXFILESIZE = 1024

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
                    self.serverAddress = str(arg)
                elif opt == '-p':
                    self.serverPort = int(arg)
                elif opt == '-d':
                    _debug = True
                    debugLog("Maximum Verbosity!")

        self.sock = EVIL.Evil()
        self.sock.bind('', 0) ##tells os to bind to all hostnames on this machine with a chosen available port
        debugLog("socket bound to: " + self.sock.sock.getsockname()[0] + ":" + str(self.sock.sock.getsockname()[1]))



    def connect(self):
        self.connection = self.sock.connect(self.serverAddress, self.serverPort)
        self.connected = True
        debugLog("created connection with " + self.connection.otherAddress[0] + ":" + str(self.connection.otherAddress[1]))

    def get(self, F):
        if self.connected:
            self.connection.send("get")
            ans = self.connection.get(1024)
            if ans == "readyget":
                f = open(F, 'w')
                self.connection.send(F)
                debugLog("sent file request to server")
                f.write(self.connection.get(MAXFILESIZE))
                f.close()
                debugLog("File Transfer Complete")
                return True
            else:
                debugLog("server did not respond with 'readyget' to 'get' request, file may not exist")
                return False
        else:
            raise UnboundLocalError('Client has no connection to a server, cannot fetch')

    def post(self, F):
        if not os.path.isfile(F):
            debugLog("Passed filename wasn't a file")
            return False

        if self.connected:
            self.connection.send("post")
            ans = self.connection.get(1024)
            if ans == "readypost":
                self.connection.send(F)
                ans = self.connection.get(1024)
                if ans == F:
                    debugLog("server ready to receive and acknowledged filename")
                    f = open(F, 'r')
                    self.connection.send(f.read(MAXFILESIZE))
                    debugLog("sent file post to server")
                    f.close()
                    debugLog("File Transfer Complete")
                    return True
                else:
                    debugLog("server did not correctly acknowledge filename")
                    return False
            else:
                debugLog("server did not respond with 'readypost' to 'post' request")
                return False
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
    print("APPCONNECTEDDDDDDDDDDDDDDDDDDDDDD")
    os.remove("file.txt")
    os.remove("file2.txt")
    f = open("file.txt", 'w')
    f.write("Hello, World!")
    f.close()
    app.post("file.txt")
    os.rename("file.txt", "file2.txt")
    app.get("file.txt")
    print("APPPOOOOOSSSSSSSSSSSSSSSSSSSSSST")
    app.get("file.txt")
    print("APPGGEEEEEEEEEEEEEETTTTTTTTTTTT")

test(sys.argv[1:])
##main(sys.argv)
