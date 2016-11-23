import random

showDebugInfo = True

def debugLog(log):
    if showDebugInfo:
        print(log)

##we'll fill this out later
class EVILPacket:
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

  def __init__(self):
      self.src_port = 0
      self.dst_port = 0
      self.seq = 0
      self.ack = 0
      self.flags = 0
      self.window = 0
      self.checksum = 0
      self.data = 0

  def parseFromString(self, string):
      current = 0
      size = 2

      size = 2
      self.src_port = getFromBytes(current, size, string)
      current += size

      self.dst_port = getFromBytes(current, size, string)
      current += size

      self.seq = getFromBytes(current, size, string)
      current += size

      size = 4
      self.ack = getFromBytes(current, size, string)
      current += size

      size = 2
      self.flags = getFromBytes(current, size, string)
      current += size

      self.window = getFromBytes(current, size, string)
      current += size

      size = 4
      self.checksum = getFromBytes(current, size, string)
      current += size

      self.data = string[current:]

      return self

  def toString(self):
      current = 0;
      size = 0;
      temp = bytearray(20 + 10)
      size = 2
      temp = setInBytes(current, size, temp, self.src_port)
      current += size

      temp = setInBytes(current, size, temp, self.dst_port)
      current += size

      size = 4
      temp = setInBytes(current, size, temp, self.seq)
      current += size

      temp = setInBytes(current, size, temp, self.ack)
      current += size

      size = 2
      temp = setInBytes(current, size, temp, self.flags)
      current += size

      temp = setInBytes(current, size, temp, self.window)
      current += size

      size = 4
      temp = setInBytes(current, size, temp, self.checksum)
      current += size


      return temp + self.data

  def printSelf(self):
      debugLog( "Package reads: " +
              "\n Source Port: " +  hex(self.src_port) +
              "\n Dest Port: " +    hex(self.dst_port) +
              "\n Seq: " +          hex(self.seq) +
              "\n Ack: " +          hex(self.ack) +
              "\n Flags: " +        hex(self.flags) +
              "\n Window: " +       hex(self.window) +
              "\n Checksum: " +     hex(self.checksum) +
              "\n Data: " +         str(self.data)
              )


def getFromBytes(pos, size, string):
    temp = 0
    for offset in range(0, size):
        temp = temp << 8
        temp = temp | string[pos + offset]
    return temp

def setInBytes(pos, size, string, value):
    for offset in range(0, size):
        string[pos + offset] = (value >> (offset * 8)) & 0xFF
    return string

def test():
  pack = EVILPacket()
  pack.data = "Hello, World"
  pack.flags = int(random.getrandbits(8 * 2))
  pack.src_port = int(random.getrandbits(8 * 2))
  pack.dst_port = int(random.getrandbits(8 * 2))
  pack.seq = int(random.getrandbits(8 * 4))
  pack.ack = int(random.getrandbits(8 * 4))
  pack.window = int(random.getrandbits(8 * 2))
  pack.checksum = int(random.getrandbits(8 * 4))
  pack.printSelf()
  packString = pack.toString()
  debugLog(packString)
  newPack = EVILPacket()
  newPack = newPack.parseFromString(packString)
  newPack.printSelf()

test()
