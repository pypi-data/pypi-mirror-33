import traceback

class ExtendableError(Exception):
    def __init__(self, message = ''):
        super(message)

    @property
    def message(self):
        self.message = self.message
    
    @message.setter
    def message(self, message):
        self.message = message
    
    @message.deleter
    def message(self):
        del self.message

    @property
    def name(self):
        self.name = self.__class__.__name__

    @name.setter
    def name(self, name):
        self.name = name
    
    @name.deleter
    def name(self):
        del self.name

    if Exception.__traceback__:
        Exception(message).__traceback__

    @property
    def stack(self):
        self.stack = Exception(self.message).__traceback__

    @stack.setter
    def stack(self, stack):
        self.stack = stack

    @stack.deleter
    def stack(self):
        del stack

