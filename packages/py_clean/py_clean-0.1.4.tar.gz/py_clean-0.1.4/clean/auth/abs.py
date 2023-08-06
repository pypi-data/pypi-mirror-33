import abc

from clean.entities.token import UserToken
from clean.exceptions import AuthException


class DecodeToken(metaclass=abc.ABCMeta):

    def __init__(self, raw_token: str, scopes_check=None, resp_err_fuc=None):
        self.scopes_check = scopes_check if scopes_check is not None else {}
        self.raw_token = raw_token
        self.user_token = UserToken(username='', email='', avatar='')
        self.resp_err_func = resp_err_fuc

    @abc.abstractmethod
    def verify(self, token: str):
        """"""

    def is_valid(self) -> UserToken:
        self.decode()
        self.verify_scopes()
        return self.user_token

    def decode(self):
        token = self.raw_token
        if token is None:
            raise AuthException('token not found')
        self.user_token = self.verify(token=token)

    def verify_scopes(self):
        for key, value in self.scopes_check.items():
            if key not in self.user_token.metadata or self.user_token.metadata[key] != value:
                raise AuthException('user has not permission scopes')

    def create_resp_err(self, error_msg: str):
        if callable(self.resp_err_func):
            return self.resp_err_func(error_msg)
        else:
            return {'error': error_msg}
