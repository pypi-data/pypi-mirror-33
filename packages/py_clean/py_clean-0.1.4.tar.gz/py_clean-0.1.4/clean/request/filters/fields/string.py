from typing import Dict
from clean.request.filters.abs import BaseFilter


class StringFilter(BaseFilter):

    def __init__(self, value: str='', type_: str='eq'):
        self.value = value
        self.type = type_ if type_ != '' else 'eq'

    @classmethod
    def from_dict(cls, params: Dict, defaults: Dict=None):
        return cls(value=params.get('value', ''), type_=params.get('type', ''))

    def to_dict(self):
        return {
            'value': self.value,
            'type': self.type
        }

    def is_valid(self):
        return self.value != ''
