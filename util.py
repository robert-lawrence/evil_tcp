showDebugInfo = True

def debugLog(log):
    if showDebugInfo:
        print(log)

##we'll fill this out later
class EVILPacket:
    msg = ""
    flags = 0
    seq = 0
    ack = 0
    src_port = 0
    dst_port = 0

    def __init__(self):
      pass

    def parseFromString(self, string):
        self.msg = string[1:]
        self.flags = ord(string[0])
        return self

    def toString(self):

        return chr(self.flags) + self.msg

    def printSelf(self):
      debugLog("Flags: " + str(self.flags) + " Message: " + self.msg)

def test():
  pack = EVILPacket()
  pack.msg = "Hello, World"
  pack.flags = 1337
  pack.printSelf()
  packString = pack.toString()
  debugLog(packString)
  newPack = EVILPacket()
  newPack = newPack.parseFromString(packString)
  newPack.printSelf()

test()
