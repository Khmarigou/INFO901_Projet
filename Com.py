import threading

class Com() :
    def __init__(self):
        self.clock = 0
        self.clock_semaphore = threading.Semaphore(1)
    
    def getClock(self) :
        return self.clock

    def inc_clock(self, inc=1):
        with self.clock_semaphore :
            self.clock += inc
    