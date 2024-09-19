import threading
from messages.Message import Message
from messages.MessageTo import MessageTo
from messages.BroadcastMessage import BroadcastMessage
from Token import Token
from pyeventbus3.pyeventbus3 import *
from time import sleep

class Com() :
    def __init__(self, myId, npProcess) :
        self.clock = 0
        self.npProcess = npProcess
        self.clock_semaphore = threading.Semaphore(1)
        self.request_lock = threading.Event()
        self.token_lock = threading.Event()
        self.sync_lock = threading.Event()
        self.syncbroadcast_lock = threading.Event()
        self.boite_aux_lettre = []
        self.myId = myId
        self.etat = "null"
        self.isAlive = True
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
            if msg.getPayload() == "sync" :
                self.syncbroadcast_lock.set()
            else :
                self.change_clock(msg.getClock())
                self.boite_aux_lettre.append(msg)
    
    def sendTo(self, obj, dest) :
        self.inc_clock()
        PyBus.Instance().post(MessageTo(obj, dest, self.getClock()))

    @subscribe(threadMode = Mode.PARALLEL, onEvent=MessageTo)
    def onReceive(self, msg) :
        if msg.getDest() == self.getMyId() :
            if msg.getPayload() == "sync" :
                self.sync_lock.set()
            else :
                self.change_clock(msg.getClock())
                self.boite_aux_lettre.append(msg)
    
    def requestSC(self) :
        self.etat = "request"
        print(f"{self.getMyId()} request SC")
        self.request_lock.clear()
        self.request_lock.wait(10)
    
    def releaseSC(self) :
        self.etat = "release"
        print(f"{self.getMyId()} release SC")
        self.token_lock.set()
    
    @subscribe(threadMode = Mode.PARALLEL, onEvent=Token)
    def onToken(self, token):
        if self.isAlive :
            if token.getDest() == self.myId :
                sleep(1)
                print(f"{self.getMyId()} receives token, state : {self.etat}")
                if self.etat == "request" :
                    self.request_lock.set()
                    self.etat = "SC"
                    self.token_lock.clear()
                    self.token_lock.wait(10)
                print(f"{self.getMyId()} sends token to {(self.myId + 1) % self.npProcess}")
                token.setDest((self.myId + 1) % self.npProcess)
                PyBus.Instance().post(token)
    
    def sendFirstToken(self) :
        dest = (self.myId + 1) % self.npProcess
        print(f"sendFirstToken to {str(dest)}")
        PyBus.Instance().post(Token(dest))

    def synchronize(self) :
        if self.myId == self.npProcess -1 :
            self.sendTo("sync", self.myId - 1)
            self.syncbroadcast_lock.clear()
            self.syncbroadcast_lock.wait(10)
        elif self.myId == 0 :
            self.sync_lock.clear()
            self.sync_lock.wait(10)
            self.broadcast("sync")
        else :
            self.sync_lock.clear()
            self.sync_lock.wait(10)
            self.sendTo("sync", self.myId - 1)
            self.syncbroadcast_lock.clear()
            self.syncbroadcast_lock.wait(10)


    def stop(self):
        self.isAlive = False