import sys
import getopt
import EVIL
import threading
from util import debugLog
import os.path
import cmd
import readline
import connection

global _debug

class SESSIONSTATE():
    IDLE = 1
    GET_1 = 2
    GET_2 = 3
    POST_1 = 5
    POST_2 = 6
    POST_3 = 7

class ServerCmd(cmd.Cmd):
    def init(self, port):
        self.client = None
        self.port = port
        self.promt = "EVIL: "
        self.server = FTAserver(port) #TODO: change server init

    def do_window(self,W):
        try:
            wsize = int(W)
        except Exception as e:
            print("Error: window size must be an int!")
        self.server.window(W)
        print("Window size set to "+str(W)+"\n")

    def do_terminate(self,line):
        self.server.terminate()
        print("Server Terminated\n")

    def emptyline(self):
        pass


class FTAserver():

    def operate(self):
        while True:
            if self.sock.isClosed:
                break
            try:
                newSessionConnection = self.sock.accept(timeout=5)
            except Exception as e:
                continue
            if self.sock.isClosed:
                break
            debugLog("accepted connection from " + newSessionConnection.otherAddress[0] + ":" + str(newSessionConnection.otherAddress[1]))
            sessionThread = threading.Thread(None, self.handleSession, "session_thread", (newSessionConnection,))
            sessionThread.start()

    def handleSession(self, conn):
        debugLog("new session started with " + conn.otherAddress[0] + ":" + str(conn.otherAddress[1]))
        sessionState = SESSIONSTATE.IDLE
        filename = ""
        fileSize = 0
        while True:
            if conn.state == connection.STATE.CLOSED:
                break
            try:
                string = conn.get(1024,timeout=5)
            except Exception as e:
                continue
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
                    # conn.send("back to idle")
                    sessionState = SESSIONSTATE.IDLE
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


    def __init__(self, port):
        self.ourPort = port
        self.maxMessageSize = 1024

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
    try:
        port = int(argv[1])
    except Exception as e:
        print("Error parsing Args.\n Syntax: \"FTA-server port\"")
        return
    parser = ServerCmd()
    parser.init(port)
    parser.cmdloop()
    #return FTAserver(argv)

def test(argv):
    app = main(argv)

#test(sys.argv[1:])
main(sys.argv)
