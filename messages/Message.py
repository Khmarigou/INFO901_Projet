from abc import ABC, abstractmethod

class Message(ABC):
    
    def __init__(self, payload):
        self.payload = payload

    @abstractmethod
    def getPayload(self):
        return self.payload