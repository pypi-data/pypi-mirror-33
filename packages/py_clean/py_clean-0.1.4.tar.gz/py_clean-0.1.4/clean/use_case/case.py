import abc
import logging
from typing import Dict

from clean.entities.token import UserToken
from clean.auth.abs import DecodeToken
from clean.exceptions import RepositoryDoesNotExistException
from clean.request.inout.ports import ResponseFailureBuilder, Response, Request


class UseCaseAbs(metaclass=abc.ABCMeta):
    def execute(self, req: Request or Dict):
        if not req:
            self.logger().debug(req.errors)
            return ResponseFailureBuilder.build_from_invalid_request(req)
        try:
            return self.process_request(req=req)
        except Exception as exc:
            self.logger().exception('use case exception')
            if self.show_error():
                return ResponseFailureBuilder.build_system_error(
                    "{}: {}".format(exc.__class__.__name__, "{}".format(exc)))
            else:
                return ResponseFailureBuilder.build_system_error("Server Error, We're working to solve this issue.")

    @abc.abstractmethod
    def process_request(self, req: Request or Dict) -> Response or Dict:
        """"""

    def logger(self):
        return logging

    def show_error(self):
        return True


class BaseUseCase(UseCaseAbs):

    @abc.abstractmethod
    def custom_process(self, req: Request) -> Response:
        """"""

    def process_request(self, req: Request) -> Response:
        try:
            return self.custom_process(req)
        except RepositoryDoesNotExistException:
            oid = getattr(req, 'oid', '')
            return ResponseFailureBuilder.build_resource_error("oid = '{}' not found".format(oid))


class BaseAuthUseCase(UseCaseAbs):

    def __init__(self, usr_token: UserToken):
        self.usr_token = usr_token
        self.check_usr_token()

    def check_usr_token(self):
        if not isinstance(self.usr_token, UserToken):
            raise AttributeError('usr_token is not instance of UserToken')

    @abc.abstractmethod
    def custom_process(self, req: Request, token: UserToken) -> Response:
        """"""

    def process_request(self, req: Request) -> Response:
        try:
            return self.custom_process(req, self.usr_token)
        except RepositoryDoesNotExistException:
            oid = getattr(req, 'oid', '')
            return ResponseFailureBuilder.build_resource_error("oid = '{}' not found".format(oid))
