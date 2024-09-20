import threading
from messages.BroadcastSync import BroadcastSync
from messages.Message import Message
from messages.MessageSync import MessageSync
from messages.MessageTo import MessageTo
from messages.BroadcastMessage import BroadcastMessage
from Token import Token
from pyeventbus3.pyeventbus3 import *
from time import sleep

class Com() :
    '''
    Communication class for the middleware
    Input :
        myId : int : id of the process
        npProcess : int : number total of process
    '''
    def __init__(self, myId : int, npProcess) :
        self.clock = 0
        self.npProcess = npProcess
        self.clock_semaphore = threading.Semaphore(1)
        self.request_lock = threading.Event()
        self.token_lock = threading.Event()
        self.sync_lock = threading.Event()
        self.syncbroadcast_lock = threading.Event()
        self.syncSender_lock = threading.Event()
        self.syncReceiver_lock = threading.Event()
        self.boite_aux_lettre = []
        self.myId = myId
        self.etat = "null"
        self.isAlive = True
        PyBus.Instance().register(self, self)
    
    def getMyId(self) -> int :
        '''
        Return the id of the process
        '''
        return self.myId
    
    def getClock(self) -> int :
        '''
        Return the Lamport clock of the process
        '''
        return self.clock

    def inc_clock(self, inc=1) -> None:
        '''
        Increment the Lamport clock by inc, default value is 1
        '''
        with self.clock_semaphore :
            self.clock += inc
    
    def change_clock(self, clock) -> None :
        '''
        Change the Lamport clock to the max between the current clock and a new clock received, then increment by 1
        '''
        with self.clock_semaphore :
            self.clock = max(self.clock, int(clock)) + 1
    
    def getMessage(self) -> None | any :
        '''
        Return the first message in the mailbox
        '''
        if len(self.boite_aux_lettre) > 0 :
            msg = self.boite_aux_lettre.pop(0)
            return msg.getPayload()
        return None
    
    def getNumberMessage(self) -> int :
        '''
        Return the number of message in the mailbox
        '''
        return len(self.boite_aux_lettre)
    
    def broadcast(self, obj) -> None :
        '''
        Send a message to all process except itself
        Input :
            obj : any : payload of the message to send
        '''
        self.inc_clock()
        msg = BroadcastMessage(self.getMyId(), obj, self.getClock())
        PyBus.Instance().post(msg)

    @subscribe(threadMode = Mode.PARALLEL, onEvent=BroadcastMessage)
    def onBroadcast(self, msg) -> None:
        '''
        Receive a broadcast message and add it to the mailbox
        '''
        if msg.getSender() != self.getMyId() :
            if msg.getPayload() == "sync" :
                self.syncbroadcast_lock.set()
            else :
                self.change_clock(msg.getClock())
                self.boite_aux_lettre.append(msg)
    
    def sendTo(self, obj, dest) -> None :
        '''
        Send a message to a specific process
        Input :
            obj : any : payload of the message to send
            dest : int : id of the process to send the message
        '''
        self.inc_clock()
        PyBus.Instance().post(MessageTo(obj, dest, self.getClock()))

    @subscribe(threadMode = Mode.PARALLEL, onEvent=MessageTo)
    def onReceive(self, msg) -> None :
        '''
        Receive a dedicated message and add it to the mailbox
        '''
        if msg.getDest() == self.getMyId() :
            if msg.getPayload() == "sync" :
                self.sync_lock.set()
            else :
                self.change_clock(msg.getClock())
                self.boite_aux_lettre.append(msg)
    
    def requestSC(self) -> None :
        '''
        Request the access to the critical section, block until the process receive the token
        '''
        self.etat = "request"
        print(f"{self.getMyId()} request SC")
        self.request_lock.clear()
        self.request_lock.wait(10)
    
    def releaseSC(self) -> None :
        '''
        Release the access to the critical section
        '''
        self.etat = "release"
        print(f"{self.getMyId()} release SC")
        self.token_lock.set()
    
    @subscribe(threadMode = Mode.PARALLEL, onEvent=Token)
    def onToken(self, token) -> None :
        '''
        Receive a token, if the process requested the critical section it will keep the token until the end of the critical section,
        otherwise or when the process exit the critical section, it will send the token to the next process
        '''
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
    
    def sendFirstToken(self) -> None :
        '''
        Send the first token to the next process
        '''
        dest = (self.myId + 1) % self.npProcess
        print(f"sendFirstToken to {str(dest)}")
        PyBus.Instance().post(Token(dest))

    def synchronize(self) -> None :
        '''
        Synchronize all process, the process wait until all process are synchronized before continue
        '''
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
    
    def broadcastSync(self, obj, sender) -> None :
        '''
        Send a synchronization message to all process except the sender
        Input :
            obj : any : payload of the message to send
            sender : int : id of the process that send the message
        '''
        if self.myId == sender :
            self.inc_clock()
            msg = BroadcastSync(self.getMyId(), obj, self.getClock())
            PyBus.Instance().post(msg)
            self.synchronize()
    
    @subscribe(threadMode = Mode.PARALLEL, onEvent=BroadcastSync)
    def onBroadcastSync(self, msg) -> None :
        '''
        Receive a synchronization message and add it to the mailbox
        '''
        if msg.getSender() != self.getMyId() :
            self.change_clock(msg.getClock())
            self.boite_aux_lettre.append(msg)
            self.synchronize()
        
    def sendToSync(self, obj, dest) -> None :
        '''
        Send a synchronization message to a specific process
        Input :
            obj : any : payload of the message to send
            dest : int : id of the process to send the message
        '''
        self.inc_clock()
        PyBus.Instance().post(MessageSync(obj, dest, self.getClock()))
        self.syncSender_lock.clear()
        self.syncSender_lock.wait(10)
    
    def recevFromSync(self, msg, sender) -> None :
        '''
        Receive a synchronization message and add it to the mailbox
        Input :
            obj : any : payload of the message to send
            sender : int : id of the process that send the message
        '''
        self.syncReceiver_lock.clear()
        self.syncReceiver_lock.wait(10)
        self.change_clock(msg.getClock())
        self.boite_aux_lettre.append(msg)
        PyBus.Instance().post(MessageSync("OK", sender, self.getClock()))
    
    @subscribe(threadMode = Mode.PARALLEL, onEvent=MessageSync)
    def onReceiveSync(self, msg) -> None :
        '''
        Receive a synchronization message and unlock process
        '''
        if msg.getDest() == self.getMyId() :
            self.change_clock(msg.getClock())
            self.boite_aux_lettre.append(msg)
            self.syncSender_lock.set()
            

    def stop(self):
        self.isAlive = False