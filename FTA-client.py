import sys
import getopt
import EVIL
import threading
from util import debugLog
import os.path
import cmd
import readline

MAXFILESIZE = 1024000

class ClientCmd(cmd.Cmd):
    def init(self, address, port):
        self.client = None
        self.address = address
        self.port = port
        self.promt = "EVIL: "
        self.client = FTAclient(address,port) #TODO change server init

    def do_window(self,W):
        try:
            wsize = int(W)
        except Exception as e:
            print("Error: window size must be an int!")
        self.client.window(W)
        print("Window size set to "+str(W)+"\n")

    def do_connect(self,line):
        self.client.connect()

    def do_get(self,line):
        self.client.get(line)
    
    def do_post(self,line):
        self.client.post(line)

    def do_disconnect(self,line):
        self.client.terminate()
        print("Server Terminated\n")
        return True

    def emptyline(self):
        pass

    def do_EOF(self,line):
        self.client.terminate()
        return True


class FTAclient():

    def __init__(self, address, port):
        self.serverAddress = address
        self.serverPort = port
        self.maxMessageSize = 1024
        self.connected = False

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
            if ans == "get":
                self.connection.send(F)
                debugLog("sent file request to server")
                ans = self.connection.get(1024)
                if ans[0:8] == "got it: ":
                    fileSize = int(ans[8:])
                    self.connection.send("send file")
                    f = open(F, 'w')
                    fileData = ""
                    while len(fileData) < fileSize:
                        fileData += self.connection.get(MAXFILESIZE)
                    # could debug, make sure len is exactly right
                    f.write(fileData)
                    f.close()
                    print("File Transfer Complete")
                    return True
                else:
                    print("server did not acknowledge filename, may not be on server")
                    return False

            else:
                debugLog("server did not respond with 'get' to get request, may be in the wrong state")
                print("Error fetching file")
                return False
        else:
            print('Client has no connection to a server, cannot fetch')

    def post(self, F):
        if not os.path.isfile(F):
            debugLog("Passed filename wasn't a file")
            return False

        if self.connected:
            f = open(F,'r')
            fileSize = len(f.read())
            f.close()
            self.connection.send("post: "+str(fileSize))
            ans = self.connection.get(1024)
            if ans == "post":
                self.connection.send(F)
                ans = self.connection.get(1024)
                if ans == "send file":
                    debugLog("server ready to receive")
                    f = open(F, 'r')
                    self.connection.send(f.read())
                    debugLog("sent file post to server")
                    f.close()
                    print("File Transfer Complete")
                    return True
                else:
                    print("server did not correctly acknowledge for receipt of file\n")
                    return False
            else:
                debugLog("server did not respond with 'post' to 'post' request")
                print("Error sending file\n")
                return False
        else:
            print('Client has no connection to a server, cannot fetch\n')

    def window(self, W):
        self.sock.setMaxWindowSize(W)

    def terminate(self):
        self.sock.close()
        debugLog("Client Closed")
        sys.exit()


def main(argv):
    try:
        address = argv[1]
        port = int(argv[2])
    except Exception as e:
        print("Error parsing Args.\n Syntax: \"FTA-client address port\"")
        return
    parser = ClientCmd()
    parser.init(address,port)
    parser.cmdloop()
    #return FTAclient(argv)

def test(argv):
    app = main(argv)
    app.connect()
    print("APPCONNECTEDDDDDDDDDDDDDDDDDDDDDD")
    '''
    if os.path.isfile("file.txt"):
        os.remove("file.txt")
    if os.path.isfile("file2.txt"):
        os.remove("file2.txt")
    f = open("file.txt", 'w')
    f.write("Hello, World!")
    f.close()
    '''
    app.get("killstreak.png")
    ##os.rename("file.txt", "file2.txt")
    print("APPPOOOOOSSSSSSSSSSSSSSSSSSSSSST")
    print("APPGGEEEEEEEEEEEEEETTTTTTTTTTTT")
    ##app.terminate()

#test(sys.argv[1:])
main(sys.argv)
