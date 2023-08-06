from random import sample

class Message(object):
    def __init__(self, target, source, msn, cmd, payload):
        self.target = target
        self.source = source
        self.msn = msn
        self.cmd = cmd 
        self.payload = payload

    @property
    def data(self):
        plen = len(self.payload)
        filler = [0] * (65-plen-8)
        full = [0x0] + self.target + self.source + \
            [self.msn, self.cmd, plen] + self.payload + filler
        return full

class Ping(Message):
    def __init__(self, target, source):

        super().__init__(target, source, 0x00, 0x00, [])