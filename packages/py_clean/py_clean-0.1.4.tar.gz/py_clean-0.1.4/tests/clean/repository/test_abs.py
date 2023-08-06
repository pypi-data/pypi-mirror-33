from inspect import ismethod, isabstract, signature
from unittest import mock

from clean.repository.abs import BaseGateway, BaseFactory, BaseRepository, BaseListRepository


def test_gateway_abs_has_methods_init_and_down():
    r = BaseGateway()

    assert ismethod(r.init)
    assert ismethod(r.down)


def test_factory_abs_is_abstract_class():
    assert isabstract(BaseFactory)


def test_factory_abs_has_create_method_as_abstract():
    ab = BaseFactory.__abstractmethods__
    sig = str(signature(BaseFactory.create))

    assert ab == frozenset(['create'])
    assert sig == '(self, raw)'


def test_repository_interface_has_attributes_gateway_and_factory():
    factory = mock.Mock()
    gate = mock.Mock()
    repo = BaseRepository(gateway=gate, factory=factory)

    assert hasattr(repo, 'gateway')
    assert hasattr(repo, 'factory')


def test_base_list_repository_calls_all():
    factory = mock.Mock()
    gate = mock.Mock()
    repo = BaseListRepository(gateway=gate, factory=factory)
    repo.all()

    assert gate.list.call_count == 1
    assert gate.list.call_args == mock.call()
