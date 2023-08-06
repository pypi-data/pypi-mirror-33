class ErrorMessage:
    __slots__ = ['type', 'message']

    def __init__(self, type_: str, message: str):
        self.type = type_
        self.message = message

    def __repr__(self):
        return "{}: {}".format(self.type, self.message)

    def __eq__(self, other):
        return self.type == other.type and self.message == other.message

    @classmethod
    def from_dict(cls, raw):
        return cls(type_=raw['type'], message=raw['message'])
