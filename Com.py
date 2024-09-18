import threading
from messages.Message import Message
from messages.MessageTo import MessageTo
from messages.BroadcastMessage import BroadcastMessage
from pyeventbus3.pyeventbus3 import *

class Com() :
    def __init__(self):
        self.clock = 0
        self.clock_semaphore = threading.Semaphore(1)
        self.boite_aux_lettre = []
    
    def getClock(self) :
        return self.clock

    def inc_clock(self, inc=1):
        with self.clock_semaphore :
            self.clock += inc
    
    def change_clock(self, clock) :
        with self.clock_semaphore :
            self.clock = max(self.clock, clock) + 1
    
    def getMessage(self) :
        return self.boite_aux_lettre.pop(0)
    
    def broadcast(self, obj) :
        self.inc_clock()
        msg = BroadcastMessage(self.getMyId(), obj, self.getClock())
        PyBus.Instance().post(msg)

    @subscribe(threadMode = Mode.PARALLEL, onEvent=BroadcastMessage)
    def onBroadcast(self, msg) :
        if msg.getSender() != self.getMyId() :
            self.change_clock(msg.getClock())
            self.boite_aux_lettre.append(msg)
    
    def sendTo(self, obj, receiver) :
        self.inc_clock()
        PyBus.Instance().post(Message(self.getMyId(), receiver, obj))

    @subscribe(threadMode = Mode.PARALLEL, onEvent=MessageTo)
    def onReceive(self, msg) :
        if msg.getDest() == self.getMyId() :
            self.change_clock(msg.getClock())
            self.boite_aux_lettre.append(msg)
    
    