class ArgumentError(Exception):
    def __init__(self, message, fn):
        self.message = message
        self.fn = fn
