import pytest

from clean.repository.abs import BaseGateway
from clean.exceptions import RepositoryException


def test_raises_for_save():
    gate = BaseGateway()

    with pytest.raises(RepositoryException) as e:
        gate.save({})

    assert str(e.value) == 'save gateway not implemented yet'


def test_raises_for_get():
    gate = BaseGateway()

    with pytest.raises(RepositoryException) as e:
        gate.get(oid='1234567890')

    assert str(e.value) == 'get gateway not implemented yet'


def test_raises_for_update():
    gate = BaseGateway()

    with pytest.raises(RepositoryException) as e:
        gate.update(oid='1234567890', raw_attributes={})

    assert str(e.value) == 'update gateway not implemented yet'


def test_raises_for_delete():
    gate = BaseGateway()

    with pytest.raises(RepositoryException) as e:
        gate.delete(oid='1234567890')

    assert str(e.value) == 'delete gateway not implemented yet'


def test_gateway_list_return_empty_list():
    gate = BaseGateway()
    res = gate.list()

    assert res == []


def test_gateway_limit():
    gate = BaseGateway()
    res = gate.limit([], offset=1, limit=100)

    assert res == []


def test_gateway_sort():
    gate = BaseGateway()
    res = gate.sort([], sort_by=[''])

    assert res == []
