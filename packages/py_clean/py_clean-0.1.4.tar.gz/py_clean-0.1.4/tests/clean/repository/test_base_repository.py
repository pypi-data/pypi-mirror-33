import pytest
from unittest import mock

from clean.repository.abs import BaseGateway, BaseRepository, BaseListRepository, BaseFactory
from clean.exceptions import RepositoryException


class Entity:

    def __init__(self, oid: str, name: str, age: int):
        self.oid = oid
        self.name = name
        self.age = age

    @classmethod
    def from_dict(cls, params):
        return cls(oid=params['oid'], name=params['name'], age=params['age'])

    def to_dict(self):
        return {
            'oid': self.oid,
            'name': self.name,
            'age': self.age
        }


class EntityFactory(BaseFactory):

    def create(self, raw):
        return Entity.from_dict(raw)


@pytest.fixture
def entities():
    return [
        Entity('1234567890', name='0', age=0).to_dict(),
        Entity('1234567891', name='1', age=1).to_dict(),
        Entity('1234567892', name='2', age=2).to_dict(),
        Entity('1234567893', name='3', age=3).to_dict(),
    ]


def test_repo_save():
    entity = Entity(oid='06832f856fcd', name='crl', age=20)
    gateway = mock.Mock(spec=BaseGateway)
    gateway.save.return_value = entity.to_dict()

    factory = EntityFactory()
    repo = BaseRepository(gateway=gateway, factory=factory)

    res = repo.save(entity=entity)

    assert bool(res) is True
    assert gateway.save.call_count == 1
    assert gateway.save.call_args == mock.call(dict_obj=entity.to_dict())
    assert res.to_dict() == entity.to_dict()


def test_repo_save_gateway_error():
    entity = Entity(oid='06832f856fcd', name='crl', age=20)
    gateway = mock.Mock(spec=BaseGateway)
    gateway.save.side_effect = RepositoryException('cannot be saved')

    factory = EntityFactory()
    repo = BaseRepository(gateway=gateway, factory=factory)

    with pytest.raises(RepositoryException) as e:
        repo.save(entity=entity)

    assert gateway.save.call_count == 1
    assert gateway.save.call_args == mock.call(dict_obj=entity.to_dict())
    assert str(e.value) == 'cannot be saved'


def test_repo_get():
    oid = '06832f856fcd'
    entity = Entity(oid='06832f856fcd', name='crl', age=20)
    gateway = mock.Mock(spec=BaseGateway)

    gateway.get.return_value = entity.to_dict()
    factory = EntityFactory()
    repo = BaseRepository(gateway=gateway, factory=factory)

    res = repo.get(oid=oid)

    assert gateway.get.call_count == 1
    assert gateway.get.call_args == mock.call(oid=oid)
    assert res.to_dict() == entity.to_dict()


def test_repo_get_not_found():
    oid = '06832f856fcd'
    gateway = mock.Mock(spec=BaseGateway)

    gateway.get.side_effect = RepositoryException('object does not exist in db')
    factory = EntityFactory()
    repo = BaseRepository(gateway=gateway, factory=factory)

    with pytest.raises(RepositoryException) as e:
        repo.get(oid=oid)

    assert gateway.get.call_count == 1
    assert gateway.get.call_args == mock.call(oid=oid)
    assert str(e.value) == 'object does not exist in db'


def test_repo_delete():
    oid = '06832f856fcd'
    entity = Entity(oid='06832f856fcd', name='crl', age=20)
    gateway = mock.Mock(spec=BaseGateway)
    gateway.delete.return_value = entity.to_dict()

    factory = EntityFactory()
    repo = BaseRepository(gateway=gateway, factory=factory)

    res = repo.delete(oid=oid)

    assert gateway.delete.call_count == 1
    assert gateway.delete.call_args == mock.call(oid=oid)
    assert res.to_dict() == entity.to_dict()


def test_repo_delete_object_not_found():
    oid = '06832f856fcd'
    gateway = mock.Mock(spec=BaseGateway)
    gateway.delete.side_effect = RepositoryException('object does not exist in db')

    factory = EntityFactory()
    repo = BaseRepository(gateway=gateway, factory=factory)

    with pytest.raises(RepositoryException) as e:
        repo.delete(oid=oid)

    assert gateway.delete.call_count == 1
    assert gateway.delete.call_args == mock.call(oid=oid)
    assert str(e.value) == 'object does not exist in db'


def test_repo_update_object():
    entity = Entity(oid='06832f856fcd', name='grl', age=20)
    gateway = mock.Mock(spec=BaseGateway)
    gateway.update.return_value = entity.to_dict()

    factory = EntityFactory()
    repo = BaseRepository(gateway=gateway, factory=factory)

    res = repo.update(oid='06832f856fcd', attributes={'name': 'grl'})

    assert gateway.update.call_count == 1
    assert gateway.update.call_args == mock.call(oid='06832f856fcd', raw_attributes={'name': 'grl'})
    assert res.to_dict() == entity.to_dict()


def test_repo_empty_list():
    gateway = mock.Mock(spec=BaseGateway)
    gateway.list.return_value = []
    factory = EntityFactory()
    repo = BaseRepository(gateway=gateway, factory=factory)

    res = repo.list()

    assert gateway.list.call_count == 1
    assert gateway.list.call_args == mock.call()
    assert len(res) == 0


def test_repo_list():
    gateway = mock.Mock(spec=BaseGateway)
    gateway.list.return_value = entities()
    factory = EntityFactory()
    repo = BaseRepository(gateway=gateway, factory=factory)

    res = repo.list()

    assert gateway.list.call_count == 1
    assert gateway.list.call_args == mock.call()
    assert len(res) == 4


def test_repo_list_limit():
    gateway = mock.Mock(spec=BaseGateway)
    gateway.limit.return_value = []
    factory = EntityFactory()
    repo = BaseListRepository(gateway=gateway, factory=factory)

    page = dict(offset=1, limit=100)
    res = repo.limit(qs=[], page=page)

    assert gateway.limit.call_count == 1
    assert gateway.limit.call_args == mock.call(qs=[], offset=1, limit=100)
    assert len(res) == 0


def test_repo_list_sort():
    gateway = mock.Mock(spec=BaseGateway)
    gateway.sort.return_value = []
    factory = EntityFactory()
    repo = BaseListRepository(gateway=gateway, factory=factory)

    sort = dict(by='')
    res = repo.sort(qs=[], sort=sort)

    assert gateway.sort.call_count == 1
    assert gateway.sort.call_args == mock.call(qs=[], sort_by=[''])
    assert len(res) == 0
