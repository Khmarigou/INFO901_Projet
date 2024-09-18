import threading
from messages.Message import Message
from messages.MessageTo import MessageTo
from messages.BroadcastMessage import BroadcastMessage
from pyeventbus3.pyeventbus3 import *

class Com() :
    def __init__(self, myId):
        self.clock = 0
        self.clock_semaphore = threading.Semaphore(1)
        self.boite_aux_lettre = []
        self.myId = myId
        PyBus.Instance().register(self, self)
    
    def getMyId(self) :
        return self.myId
    
    def getClock(self) :
        return self.clock

    def inc_clock(self, inc=1):
        with self.clock_semaphore :
            self.clock += inc
    
    def change_clock(self, clock) :
        with self.clock_semaphore :
            self.clock = max(self.clock, int(clock)) + 1
    
    def getMessage(self) :
        if len(self.boite_aux_lettre) > 0 :
            msg = self.boite_aux_lettre.pop(0)
            return msg.getPayload()
        return None
    
    def getNumberMessage(self) :
        return len(self.boite_aux_lettre)
    
    def broadcast(self, obj) :
        self.inc_clock()
        msg = BroadcastMessage(self.getMyId(), obj, self.getClock())
        PyBus.Instance().post(msg)

    @subscribe(threadMode = Mode.PARALLEL, onEvent=BroadcastMessage)
    def onBroadcast(self, msg) :
        if msg.getSender() != self.getMyId() :
            self.change_clock(msg.getClock())
            self.boite_aux_lettre.append(msg)
    
    def sendTo(self, obj, dest) :
        self.inc_clock()
        PyBus.Instance().post(MessageTo(obj, dest, self.getClock()))

    @subscribe(threadMode = Mode.PARALLEL, onEvent=MessageTo)
    def onReceive(self, msg) :
        if msg.getDest() == self.getMyId() :
            self.change_clock(msg.getClock())
            self.boite_aux_lettre.append(msg)
    
    