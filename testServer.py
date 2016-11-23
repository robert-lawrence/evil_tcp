import sys
import getopt
import EVIL

global _debug


def main(argv):

    ourAddress = "127.0.0.1"
    ourPort = 1
    maxMessageSize = 1024

    global _debug

    try:
        opts, args = getopt.getop(argv, "a:p:d")
    except getopt.GetopError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
            if opt == '-a':
                ourAddress = arg
            elif opt == '-p':
                ourPort = arg
            elif opt == '-d':
                _debug = True
                debugLog("Maximum Verbosity!")

    sock = EVIL()
    sock.bind(ourAddress, ourPort)
    debugLog("socket bound to: " + ourAddress + ":" + str(ourPort))
    conn = sock.accept()
    debugLog("accepted connection from " + conn.otherAddress[0] + ":" + str(conn.otherAddress[1]))
    string = conn.get(maxMessageSize)
    debugLog("received " + string + " from "+ conn.otherAddress[0] + ":" + str(conn.otherAddress[1]))
    reply = string.upper()
    debugLog("replying to " + conn.otherAddress[0] + ":" + str(conn.otherAddress[1]) + " with: " + reply)
    conn.send(reply)

main(sys.argv)
