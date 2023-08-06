from clean.utils.unique import UUIDGenerator

from clean.exceptions import FilterDoesNotExist
from clean.request.inout.ports import Response, Request, ResponseFailureBuilder
from clean.request.inout.actions import ListRequest, DeleteRequest

from clean.use_case.case import BaseUseCase
from clean.repository.abs import BaseRepository, BaseListRepository


class SaveUseCase(BaseUseCase):
    def __init__(self, repo: BaseRepository, oid_gen=UUIDGenerator()):
        self.repo = repo
        self.oid_gen = oid_gen

    def create_entity(self, req: Request):
        raise NotImplementedError('created_entity is not implemented')

    def custom_process(self, req: Request) -> Response:
        entity = self.create_entity(req)
        result = self.repo.save(entity=entity)
        return Response(result)


class RetrieveUseCase(BaseUseCase):

    def __init__(self, repo: BaseRepository):
        self.repo = repo

    def custom_process(self, req) -> Response:
        result = self.repo.get(oid=req.oid)
        return Response(result)


class UpdateUseCase(BaseUseCase):
    def __init__(self, repo: BaseRepository):
        self.repo = repo

    def custom_process(self, req: Request) -> Response:
        params = req.to_dict()
        oid = params.pop('oid')
        result = self.repo.update(oid=oid, attributes=params)
        return Response(result)


class DeleteUseCase(BaseUseCase):
    def __init__(self, repo: BaseRepository):
        self.repo = repo

    def custom_process(self, req: DeleteRequest) -> Response:
        result = self.repo.delete(oid=req.oid)
        return Response(result)


class ListUseCase(BaseUseCase):
    def __init__(self, repo: BaseListRepository):
        self.repo = repo

    def custom_process(self, req: ListRequest) -> Response:
        try:
            result = self.repo.execute(req.ft, req.filters, req.page, req.sort)
            return Response(result)
        except FilterDoesNotExist:
            return ResponseFailureBuilder.build_parameters_error('Filter', 'filter="{}" does not exists'.format(req.ft))
