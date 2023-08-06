from typing import Dict


class Page:
    __slots__ = ['offset', 'limit']

    def __init__(self, offset: int=0, limit: int=100):
        self.offset = offset
        self.limit = limit

    @classmethod
    def from_dict(cls, params: Dict):
        return cls(offset=params.get('offset', 0),
                   limit=params.get('limit', 10))


class Sort:
    __slots__ = ['by']

    def __init__(self, by: str=''):
        self.by = by

    @classmethod
    def from_dict(cls, params: Dict):
        return cls(by=params.get('by', ''))
