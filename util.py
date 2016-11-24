import random
import sys
import hashlib
import time
import threading
import struct

class FLAG():
    FIN = 1 << 15
    SYN = FIN >> 1
    ACK = SYN >> 1
    RET = ACK >> 1

def debugLog(log):
    if  '-d' in sys.argv:
        print(" Thread: " +  str(threading.current_thread().name) + " " + log)


class EVILPacket():
    '''
        0                   1                   2                   3
      0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
     |          Source Port          |       Destination Port        |
     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
     |                        Sequence Number                        |
     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
     |                    Acknowledgment Number                      |
     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
     |                        |A|S|F||                               |
     |  Reserved              |C|Y|I||             Window            |
     |                        |K|N|N||                               |
     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
     |                            Checksum                           |
     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
     |                             data                              |
     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    '''
    structFormat = '!HHIIHHI'
    def __init__(self):
        self.src_port = 0
        self.dst_port = 0
        self.seq = 0
        self.ack = 0
        self.flags = 0
        self.window = 0
        self.checksum = 0
        self.data = ""

    def parseFromString(self, string):
        size = struct.calcsize(self.structFormat)
        temp = struct.unpack(self.structFormat, string[:size])
        self.src_port = temp[0]
        self.dst_port = temp[1]
        self.seq = temp[2]
        self.ack = temp[3]
        self.flags = temp[4]
        self.window = temp[5]
        self.checksum = temp[6]
        self.data = string[size:]
        return self

    def toString(self):
        return struct.pack(self.structFormat, self.src_port, self.dst_port, self.seq, self.ack, self.flags, self.window, self.checksum) + str(self.data)

    def printSelf(self):
        debugLog( "Packet reads: " +
            "\n Source Port: " +  hex(self.src_port) +
            "\n Dest Port: " +    hex(self.dst_port) +
            "\n Seq: " +          hex(self.seq) +
            "\n Ack: " +          hex(self.ack) +
            "\n Flags: " +        hex(self.flags) +
            "\n Window: " +       hex(self.window) +
            "\n Checksum: " +     hex(self.checksum) +
            "\n Data: " +         str(self.data)
              )

    def generateCheckSum(self):
        checksum = hashlib.md5()
        checksum.update(str(self.src_port))
        checksum.update(str(self.dst_port))
        checksum.update(str(self.seq))
        checksum.update(str(self.ack))
        checksum.update(str(self.flags))
        checksum.update(str(self.window))
        checksum.update(self.data)
        return int(int(checksum.hexdigest(), 16) & 0xFFFFFFFF)

    def validateCheckSum(self):
        currentCheckSum = self.generateCheckSum()
        return (currentCheckSum == self.checksum)

    def checkFlag(self, flag):
        return (self.flags & flag) > 0

    def setFlag(self, flag, tf=True):
        if tf:
            self.flags = self.flags | flag
        else:
            self.flags = self.flags & ~flag

def getFromBytes(pos, size, string):
    temp = 0
    for offset in range(0, size):
        temp = temp << 8
        temp = temp | int(string[pos + offset])
    return temp

def setInBytes(pos, size, string, value):
    for offset in range(0, size):
        if type(value) is str:
            string[pos + offset] = ord(value[offset])
        else:
            string[pos + size - offset - 1] = (value >> (offset * 8)) & 0xFF
    return string
def test():
    pack = EVILPacket()
    pack.data = "sbutt"
    random.seed(5)
    pack.flags = int(random.getrandbits(8 * 2))
    pack.src_port = int(random.getrandbits(8 * 2))
    pack.dst_port = int(random.getrandbits(8 * 2))
    pack.seq = int(random.getrandbits(8 * 4))
    pack.ack = int(random.getrandbits(8 * 4))
    pack.window = int(random.getrandbits(8 * 2))
    pack.checksum = int(random.getrandbits(8 * 4))
    pack.printSelf()
    packString = pack.toString()
    ##debugLog(packString.decode(encoding='windows-1252'))
    debugLog(hex(pack.generateCheckSum()))
    newPack = EVILPacket()
    newPack = newPack.parseFromString(packString)
    newPack.printSelf()
    debugLog(hex(newPack.generateCheckSum()))

    newPackString = newPack.toString()
    newNewPack = EVILPacket()
    newNewPack = newNewPack.parseFromString(newPackString)
    newNewPack.printSelf()
    debugLog(hex(newNewPack.generateCheckSum()))
