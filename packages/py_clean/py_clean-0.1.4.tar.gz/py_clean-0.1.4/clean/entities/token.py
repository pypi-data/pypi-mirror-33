from typing import Dict


class UserToken:
    __slots__ = ['username', 'email', 'avatar', 'metadata']

    def __init__(self, username: str, email: str, avatar: str, metadata: Dict={}):
        self.username = username
        self.email = email
        self.avatar = avatar
        self.metadata = metadata

    @classmethod
    def from_dict(cls, raw: Dict):
        return cls(username=raw['username'],
                   email=raw['email'],
                   avatar=raw['avatar'],
                   metadata=raw.get('metadata', {}))

    def __eq__(self, other):
        return self.username == other.username

    def __repr__(self):
        return "{}: {}".format(self.username, self.metadata)
