from typing import Dict, List

from clean.entities.error import ErrorMessage

from clean.utils.requests import grouping
from clean.request.inout.ports import Request
from clean.request.inout.base import BaseInput, BaseFilterInput

from clean.exceptions import FilterException


class ErrorRespMixin:

    @classmethod
    def create_error_response(cls, errors: List[ErrorMessage]):
        res = Request()
        res.add_errors(errors)
        return res


class BaseRequest(ErrorRespMixin, BaseInput):

    @classmethod
    def from_dict(cls, params: Dict) -> 'BaseRequest' or Request:
        req = cls.SCHEMA_VERIFIER_CLS(cls.SCHEMA)
        if req.is_valid(params):
            return cls.factory(params=params)
        return cls.create_error_response(req.errors)


class ListRequest(ErrorRespMixin, BaseFilterInput):

    @classmethod
    def from_dict(cls, params: Dict) -> 'ListRequest' or Request:
        ft = params.pop('ft', 'all')
        groups = grouping(params)
        req = cls.SCHEMA_VERIFIER_CLS(cls.SCHEMA)
        if req.is_valid(groups):
            groups['ft'] = ft
            try:
                return cls.factory(params=groups)
            except FilterException as e:
                return cls.create_error_response([ErrorMessage(type_='FilterError', message=str(e))])
        return cls.create_error_response(req.errors)


class RetrieveRequest(BaseRequest):
    SCHEMA = {
        'properties': {
            'oid': {'type': 'string'}
        },
        'required': ['oid'],
    }

    def __init__(self, oid: str):
        super(RetrieveRequest, self).__init__()
        self.oid = oid

    @classmethod
    def factory(cls, params: Dict) -> 'RetrieveRequest' or Request:
        return cls(oid=params['oid'])


class DeleteRequest(BaseRequest):
    SCHEMA = {
        'properties': {
            'oid': {'type': 'string'}
        },
        'required': ['oid'],
    }

    def __init__(self, oid: str):
        super(DeleteRequest, self).__init__()
        self.oid = oid

    @classmethod
    def factory(cls, params: Dict) -> 'RetrieveRequest' or Request:
        return cls(oid=params['oid'])
