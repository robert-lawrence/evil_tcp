import sys
import getopt
import EVIL

def main(argv):

    serverAddress = "127.0.0.1"
    serverPort = 0
    ourAddress = "127.0.0.1"
    ourPort = 1
    message = "Hello, World!"
    global _debug

    try:
        opts, args = getopt.getop(argv, "a:p:s:o:m:d")
    except getopt.GetopError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
            if opt == '-a':
                ourAddress = arg
            elif opt == '-p':
                ourPort = arg
            elif opt == '-s':
                serverAddress = arg
            elif opt == '-o':
                serverPort = arg
            elif opt == '-m':
                message = arg
            elif opt == '-d':
                _debug = True

    sock = EVIL()
    sock.bind(ourAddress, ourPort)
    debugLog("socket bound to: " + ourAddress + ":" + str(ourPort))

    conn = sock.connect(serverAddress, serverPort)
    debugLog("connected to: " + serverAddress + ":" + str(serverPort))
    conn.send(message)
    debugLog("sent " + message + " to " + serverAddress + ":" + str(serverPort))

    debugLog("Got: " + conn.get(len(message)) + " from " + serverAddress + ":" + str(serverPort))

main(sys.argv)
