from typing import List, Dict

from clean.entities.error import ErrorMessage
from clean.entities import resp_status


class Request:
    def __init__(self):
        self.errors: List[ErrorMessage] = []

    def add_error(self, error: ErrorMessage):
        self.errors.append(error)

    def add_errors(self, errors: List[ErrorMessage]):
        self.errors.extend(errors)

    def to_dict(self):
        params = self.__dict__
        params.pop('errors')
        result = dict()
        for k in params.keys():
            if params[k] is not None:
                result[k] = params[k]
        return result

    @classmethod
    def from_dict(cls, params: Dict):
        raise NotImplementedError

    def __bool__(self):
        return len(self.errors) == 0


class Response:
    def __init__(self, context=None, status: str=resp_status.OK):
        self.context = context
        self.status = status
        self.errors: List[ErrorMessage] = []

    def add_error(self, error: ErrorMessage):
        self.errors.append(error)

    def add_errors(self, errors: List[ErrorMessage]):
        self.errors.extend(errors)

    @property
    def result(self):
        return self.context

    def __bool__(self):
        return len(self.errors) == 0


class ResponseFailureBuilder:

    @classmethod
    def build_resource_error(cls, message: str) -> Response:
        res = Response(status=resp_status.RESOURCE_ERROR)
        res.add_error(ErrorMessage(resp_status.RESOURCE_ERROR, message))
        return res

    @classmethod
    def build_system_error(cls, message: str) -> Response:
        res = Response(status=resp_status.SYSTEM_ERROR)
        res.add_error(ErrorMessage(resp_status.SYSTEM_ERROR, message))
        return res

    @classmethod
    def build_from_invalid_request(cls, invalid_request: Request) -> Response:
        res = Response(status=resp_status.PARAMETERS_ERROR)
        res.add_errors(invalid_request.errors)
        return res

    @classmethod
    def build_parameters_error(cls, type_, msg):
        res = Response(status=resp_status.PARAMETERS_ERROR)
        res.add_error(ErrorMessage(type_, msg))
        return res
