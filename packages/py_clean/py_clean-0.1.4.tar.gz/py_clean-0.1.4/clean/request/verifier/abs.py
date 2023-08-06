import abc
from typing import List, Dict

from clean.entities.error import ErrorMessage


class RequestVerifierAbs(metaclass=abc.ABCMeta):

    def __init__(self):
        self.errors: List[ErrorMessage] = []

    @abc.abstractmethod
    def is_valid(self, params: Dict):
        """"""
