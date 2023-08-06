import pytest
from unittest import mock
from types import SimpleNamespace

from clean.exceptions import FilterDoesNotExist
from clean.request.inout.ports import Response, Request
from clean.request.inout.filter import Page, Sort
from clean.use_case.common import SaveUseCase, RetrieveUseCase, UpdateUseCase, DeleteUseCase, ListUseCase
from clean.use_case.case import BaseUseCase

from clean.repository.abs import BaseRepository, BaseListRepository


class FakeSave(SaveUseCase):

    def create_entity(self, req):
        return SimpleNamespace(**dict(age=req.age, name=req.name))


def test_base_raises_required_custom_process():

    class Foo(BaseUseCase):
        pass


def test_base_process_request():
    request = mock.Mock(spec=Request)
    request.age = 20
    request.name = 'crl'

    class Baz(BaseUseCase):
        def custom_process(self, req) -> Response:
            return Response(context=SimpleNamespace(**dict(age=req.age, name=req.name)))

    res = Baz().custom_process(req=request)
    assert bool(res) is True
    assert res.result.name == 'crl'
    assert res.result.age == 20


def test_save_create_entity_raises():
    repo = mock.Mock(spec=BaseRepository)
    save_case = SaveUseCase(repo=repo)
    req = SimpleNamespace(**dict(name='crl', age=20))

    with pytest.raises(NotImplementedError):
        save_case.create_entity(req=req)


def test_save():
    repo = mock.Mock(spec=BaseRepository)
    save_case = FakeSave(repo=repo)
    req = SimpleNamespace(**dict(name='crl', age=20))

    res = save_case.create_entity(req=req)

    assert res.name == 'crl'
    assert res.age == 20


def test_save_repo_calls():
    repo = mock.Mock(spec=BaseRepository)
    req = SimpleNamespace(**dict(name='crl', age=20))

    save_case = FakeSave(repo=repo)
    save_case.process_request(req=req)

    assert repo.save.call_count == 1


def test_retrieve_repo_calls():
    repo = mock.Mock(spec=BaseRepository)
    req = mock.Mock()
    req.oid.return_value = '123456'

    save_case = RetrieveUseCase(repo=repo)
    save_case.process_request(req=req)

    assert repo.get.call_count == 1
    assert repo.get.call_args == mock.call(oid=req.oid)


def test_update_repo_calls():
    repo = mock.Mock(spec=BaseRepository)
    req = mock.Mock()
    req.to_dict.return_value = dict(oid='123456', age=20, name='crl')

    save_case = UpdateUseCase(repo=repo)
    save_case.process_request(req=req)

    assert repo.update.call_count == 1
    assert repo.update.call_args == mock.call(oid='123456', attributes=dict(age=20, name='crl'))


def test_delete_repo_calls():
    repo = mock.Mock(spec=BaseRepository)
    req = mock.Mock()
    req.oid.return_value = '123456'

    save_case = DeleteUseCase(repo=repo)
    save_case.process_request(req=req)

    assert repo.delete.call_count == 1
    assert repo.delete.call_args == mock.call(oid=req.oid)


def test_list_repo_calls():
    repo = mock.Mock(spec=BaseListRepository)
    req = mock.Mock()
    req.oid.return_value = '123456'
    req.ft = 'all'
    req.filters = {}
    req.page = Page()
    req.sort = Sort()

    save_case = ListUseCase(repo=repo)
    save_case.process_request(req=req)

    assert repo.execute.call_count == 1
    assert repo.execute.call_args == mock.call(req.ft, req.filters, req.page, req.sort)


def test_list_silent_repo_filer_does_not_exist_exception():
    repo = mock.Mock(spec=BaseListRepository)
    repo.execute.side_effect = FilterDoesNotExist('')
    req = mock.Mock()
    req.oid.return_value = '123456'
    req.ft = 'all'
    req.filters = {}
    req.page = Page()
    req.sort = Sort()

    save_case = ListUseCase(repo=repo)
    res = save_case.process_request(req=req)

    assert bool(res) is False
    assert repo.execute.call_count == 1
    assert repo.execute.call_args == mock.call(req.ft, req.filters, req.page, req.sort)
