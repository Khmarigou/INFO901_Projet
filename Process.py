from random import randint
from threading import Lock, Thread
from time import sleep

from Com import Com

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
        self.com = Com(self.myId)

        self.alive = True
        self.start()
        
    # @subscribe(threadMode = Mode.PARALLEL, onEvent=Bidule)
    # def process(self, event):        
    #     print(self.getName() + ' Processes event: ' + event.getMachin())
    #     self.horloge = max(self.horloge, event.getHorloge()) + 1

    def run(self):
        loop = 0
        while self.alive:
            sleep(1)
                
            if (self.getName() == "P0"):
                self.com.broadcast("coucou")
            
            if (self.getName() == "P1"):
                self.com.sendTo("salut", 0)
            
            sleep(1)
            print(f"{self.getName()} Received : {self.com.getMessage()}")

            loop+=1
        print(self.getName() + " stopped")

    

    def stop(self):
        self.alive = False

    def waitStopped(self):
        self.join()
