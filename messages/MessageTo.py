from messages.Message import Message

class MessageTo(Message) :
    def __init__(self, payload, dest, clock):
        super().__init__(payload)
        self.clock = clock
        self.dest = dest

    def getPayload(self):
        return self.payload
    
    def getClock(self):
        return self.clock
    
    def getDest(self):
        return self.dest