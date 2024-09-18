from random import randint
from threading import Lock, Thread

from time import sleep

#from geeteventbus.subscriber import subscriber
#from geeteventbus.eventbus import eventbus
#from geeteventbus.event import event

#from EventBus import EventBus

class Process(Thread):
    nbProcessCreated = 0
    def __init__(self, name, npProcess):
        Thread.__init__(self)

        self.npProcess = npProcess
        self.myId = Process.nbProcessCreated
        Process.nbProcessCreated +=1
        self.setName(name)


        self.horloge = 0

        self.token = False if self.myId == npProcess - 1 else True
        self.begin = False if self.myId == npProcess - 1 else True
        self.etat = "null"

        self.alive = True
        self.start()
        
    # @subscribe(threadMode = Mode.PARALLEL, onEvent=Bidule)
    # def process(self, event):        
    #     print(self.getName() + ' Processes event: ' + event.getMachin())
    #     self.horloge = max(self.horloge, event.getHorloge()) + 1

    def run(self):
        loop = 0
        while self.alive:
            print(self.getName() + " Loop: " + str(loop) + " Horloge: " + str(self.horloge))
            sleep(1)
            # if self.begin :
            #     self.begin = False
            #     PyBus.Instance().post(Token((self.myId + 1) % self.npProcess))

            # if self.getName() == "P1":
            #     self.horloge += 1
            #     b1 = Bidule("ga", horloge=self.horloge)
            #     b2 = Bidule("bu", horloge=self.horloge)
            #     print(self.getName() + " send: " + b1.getMachin())
            #     PyBus.Instance().post(b1)
            
            # if self.getName() == "P0":
            #     self.broadcast("coucou")

            # if self.getName() == "P2":
            #     self.sendTo("P1", "salut")

            # if self.token :
            #     self.token = False
            #     PyBus.Instance().post(Token((self.myId + 1) % self.npProcess))
            
            self.requestSC()
            print(self.getName() + " entre en SC ")
            sleep(randint(1, 5))
            print(self.getName() + " sort de SC ")
            self.releaseSC()
                

            loop+=1
        print(self.getName() + " stopped")

    # def broadcast(self, object) :
    #     self.horloge += 1
    #     message = BroadcastMessage(object, self.horloge, self.getName())
    #     print(self.getName() + " broadcast: " + message.getMessage())
    #     PyBus.Instance().post(message)
        

    # @subscribe(threadMode = Mode.PARALLEL, onEvent=BroadcastMessage)
    # def onBroadcast(self, message) :
    #     if (message.getSender() != self.getName()) :
    #         print(self.getName() + " receives: " + message.getMessage() + " from " + message.getSender())
    #         self.horloge = max(self.horloge, message.getHorloge()) + 1
    
    # def sendTo(self, dest, object) :
    #     self.horloge += 1
    #     message = MessageTo(object, dest)
    #     print(self.getName() + " send: " + message.getMessage() + " to " + message.getDest())
    #     PyBus.Instance().post(message)
    
    # @subscribe(threadMode = Mode.PARALLEL, onEvent=MessageTo)
    # def onReceive(self, message) :
    #     if (message.getDest() == self.getName()) :
    #         print(self.getName() + " receives: " + message.getMessage())
    #         self.horloge = max(self.horloge, message.getHorloge()) + 1

    # @subscribe(threadMode = Mode.PARALLEL, onEvent=Token)
    # def onToken(self, token):
    #     if token.getDest() == self.myId :
    #         print(self.getName() + " receives token")
    #         if self.etat == "request" :
    #             self.etat = "SC"
    #             while (self.etat != "release") :
    #                 sleep(1)
    #         if (self.alive) :
    #             token.setDest((self.myId + 1) % self.npProcess)
    #             PyBus.Instance().post(token)
    #             self.etat = "null"
    
    # def requestSC(self) :
    #     print(self.getName() + " request SC")
    #     self.etat = "request"
    #     while(self.etat != "SC") :
    #         sleep(1)
    
    # def releaseSC(self) :
    #     print(self.getName() + " release SC")
    #     self.etat = "release"

    def stop(self):
        self.alive = False

    def waitStopped(self):
        self.join()
