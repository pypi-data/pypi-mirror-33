import pytest

from clean.request.inout.ports import Response, Request
from clean.use_case.case import BaseAuthUseCase
from clean.entities.token import UserToken


class ThisCaseNeedUserInfo(BaseAuthUseCase):

    def custom_process(self, req: Request, token: UserToken) -> Response:
        pass


def test_auth_use_case_raises_if_not_user_token_is_passed():

    with pytest.raises(AttributeError):
        ThisCaseNeedUserInfo(usr_token={})


def test_create_auth_use_case():
    case = ThisCaseNeedUserInfo(usr_token=UserToken('', '', ''))

    assert case.usr_token.username == ''
