from inspect import isabstract
from typing import Dict

from clean.request.filters.abs import BaseFilter


class FooFilter(BaseFilter):

    def __init__(self, gte: str = "", lte: str = ""):
        self.gte = gte
        self.lte = lte

    def to_dict(self):
        return {
            'gte': self.gte,
            'lte': self.lte
        }

    def is_valid(self):
        return True

    @classmethod
    def from_dict(cls, params: Dict, defaults: Dict = None):
        return cls(gte=params.get('gte'), lte=params.get('lte'))


def test_base_filter_is_abstract_class():
    assert isabstract(BaseFilter)


def test_factory_abs_has_create_method_as_abstract():
    ab = BaseFilter.__abstractmethods__

    assert ab == frozenset(['from_dict', 'to_dict', 'is_valid'])


def test_create_filter():
    foo = FooFilter(gte='20160101000000', lte='20170101235959')

    assert foo.gte == '20160101000000'
    assert foo.lte == '20170101235959'


def test_create_from_dict():
    params = dict(gte='20160101000000', lte='20170101235959')
    foo = FooFilter.from_dict(params)

    assert foo.gte == '20160101000000'
    assert foo.lte == '20170101235959'


def test_create_filter_to_dict():
    foo = FooFilter(gte='20160101000000', lte='20170101235959')

    assert foo.to_dict()['gte'] == '20160101000000'
    assert foo.to_dict()['lte'] == '20170101235959'
