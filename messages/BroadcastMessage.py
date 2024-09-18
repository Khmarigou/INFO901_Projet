from messages.Message import Message

class BroadcastMessage(Message) :
    def __init__(self, sender, payload, clock):
        super().__init__(payload)
        self.sender = sender
        self.clock = clock

    def getSender(self) :
        return self.sender
    
    def getPayload(self):
        return self.payload
    
    def getClock(self):
        return self.clock