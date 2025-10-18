
class RepairOrder:
    def __init__(self):
        self.key = None
        self.name = None
        self.status = None
        self.created = None
        self.recieved = None
        self.machines = []
        self.hashboards = []

    def load(self, json):
        pass
    

class Machine:
    def __init__(self):
        self.key = None
        self.serial = None
        self.events = []

    def load(self, json):
        pass


class Hashboard:
    def __init__(self):
        self.key = None
        self.serial = None
        self.events = []

    def load(self, json):
        pass


class Event:
    def __init__(self):
        self.type = None
        self.assignee = None
        self.timestamp = None

        self.comment = None
        self.status = None
        self.components = None


    def load(self, json):
        pass

