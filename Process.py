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
        self.com = Com(self.myId, npProcess)

        self.alive = True
        self.start()
        
    # @subscribe(threadMode = Mode.PARALLEL, onEvent=Bidule)
    # def process(self, event):        
    #     print(self.getName() + ' Processes event: ' + event.getMachin())
    #     self.horloge = max(self.horloge, event.getHorloge()) + 1

    def run(self):
        loop = 0
        if self.myId == self.npProcess - 1 :
            self.com.sendFirstToken()
        while self.alive:
            print(self.getName() + " Loop: " + str(loop))
            sleep(1)

            if self.getName() == "P0":
                self.com.sendTo("j'appelle 2 et je te recontacte après", 1)
                self.com.requestSC()
                print("P0 in SC")
                sleep(randint(1, 5))
                self.com.releaseSC()
                print("P0 exit SC")
                
                # self.com.sendToSync("J'ai laissé un message à 2, je le rappellerai après, on se sychronise tous et on attaque la partie ?", 2)
                # self.com.recevFromSync(msg, 2)
               
                # self.com.sendToSync("2 est OK pour jouer, on se synchronise et c'est parti!",1)
                    
                # self.com.synchronize()
                    
                # self.com.requestSC()
                # if self.com.mailbox.isEmpty():
                #     print("Catched !")
                #     self.com.broadcast("J'ai gagné !!!")
                # else:
                #     msg = self.com.mailbox.getMsg();
                #     print(str(msg.getSender())+" à eu le jeton en premier")
                # self.com.releaseSC()


            if self.getName() == "P1":
                self.com.requestSC()
                print("P1 in SC")
                sleep(randint(1, 5))
                self.com.releaseSC()
                print("P1 exit SC")
                # if not self.com.mailbox.isEmpty():
                #     self.com.mailbox.getMessage()
                #     self.com.recevFromSync(msg, 0)

                #     self.com.synchronize()
                    
                #     self.com.requestSC()
                #     if self.com.mailbox.isEmpty():
                #         print("Catched !")
                #         self.com.broadcast("J'ai gagné !!!")
                #     else:
                #         msg = self.com.mailbox.getMsg();
                #         print(str(msg.getSender())+" à eu le jeton en premier")
                #     self.com.releaseSC()
                    
            # if self.getName() == "P2":
            #     self.com.recevFromSync(msg, 0)
            #     self.com.sendToSync("OK", 0)

            #     self.com.synchronize()
                    
            #     self.com.requestSC()
            #     if self.com.mailbox.isEmpty():
            #         print("Catched !")
            #         self.com.broadcast("J'ai gagné !!!")
            #     else:
            #         msg = self.com.mailbox.getMsg();
            #         print(str(msg.getSender())+" à eu le jeton en premier")
            #     self.com.releaseSC()
                

            loop+=1
        self.com.stop()
        print(self.getName() + " stopped")

    

    def stop(self):
        self.alive = False

    def waitStopped(self):
        self.join()
