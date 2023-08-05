class ArgumentError(Exception):
    def __init__(self, message, fn):
        self.message = message
        self.fn = fn


class ArgumentMismatchError(Exception):
    def __init__(self, message, fn):
        self.message = message
        self.fn = fn
