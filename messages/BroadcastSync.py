class BroadcastSync():
    def __init__(self, id, obj, clock):
        '''
        Constructor
        Input :
            id : int : id of the process that send the message
            obj : any : payload of the message to send
            clock : int : clock of the process that send the message
        '''
        self.id = id
        self.obj = obj
        self.clock = clock