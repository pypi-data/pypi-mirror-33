import abc
from typing import Dict, Any, Iterator, List

from clean.exceptions import RepositoryException
from clean.repository.list import RepoListBase


class BaseFactory(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def create(self, raw):
        pass


class BaseGateway:

    def init(self):
        pass

    def down(self):
        pass

    def save(self, dict_obj: Dict) -> Dict:
        raise RepositoryException('save gateway not implemented yet')

    def update(self, oid, raw_attributes: Dict) -> Dict:
        raise RepositoryException('update gateway not implemented yet')

    def get(self, oid: str) -> Dict:
        raise RepositoryException('get gateway not implemented yet')

    def delete(self, oid: str) -> Dict:
        raise RepositoryException('delete gateway not implemented yet')

    def list(self) -> Iterator:
        return []

    def limit(self, qs: Iterator, offset: int=0, limit: int=10000):
        return qs

    def sort(self, qs: Iterator, sort_by: List[str]=('', )):
        return qs


class BaseRepository:

    def __init__(self, gateway: BaseGateway, factory: BaseFactory):
        self.gateway = gateway
        self.factory = factory

    def create_factory(self, raw: Dict):
        return self.factory.create(raw=raw)

    def save(self, entity: Any):
        result = self.gateway.save(dict_obj=entity.to_dict())
        return self.factory.create(result)

    def get(self, oid: str):
        res = self.gateway.get(oid=oid)
        return self.factory.create(raw=res)

    def delete(self, oid: str):
        result = self.gateway.delete(oid=oid)
        return self.factory.create(result)

    def update(self, oid: str, attributes: Dict):
        res = self.gateway.update(oid=oid, raw_attributes=attributes)
        return self.factory.create(res)

    def list(self):
        return self.gateway.list()


class BaseListRepository(BaseRepository, RepoListBase):

    def all(self):
        return self.gateway.list()

    def limit(self, qs: Iterator, page: Dict):
        return self.gateway.limit(qs=qs, offset=page['offset'], limit=page['limit'])

    def sort(self, qs: Iterator, sort: Dict):
        sort_by = sort['by'].split(' ')
        return self.gateway.sort(qs=qs, sort_by=sort_by)
