import abc
from typing import Dict


class BaseFilter(metaclass=abc.ABCMeta):

    @abc.abstractclassmethod
    def from_dict(cls, params: Dict, defaults: Dict=None) -> 'BaseFilter':
        """"""

    @abc.abstractmethod
    def to_dict(self):
        """"""

    @abc.abstractmethod
    def is_valid(self):
        """"""
