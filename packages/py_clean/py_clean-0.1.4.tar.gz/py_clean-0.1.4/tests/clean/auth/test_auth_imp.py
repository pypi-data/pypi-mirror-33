import pytest

from clean.entities.token import UserToken
from clean.auth.abs import DecodeToken
from clean.exceptions import AuthException


class VerifyTokenAuth(DecodeToken):

    def verify(self, token: str):
        return UserToken('crl', 'admin@admin.com', avatar='', metadata={'foo': 'bar'})


def test_decode_token():
    vt = VerifyTokenAuth(raw_token='token_data')
    ut = vt.is_valid()
    assert ut.username == 'crl'
    assert ut.email == 'admin@admin.com'
    assert ut.avatar == ''


def test_raise_token_is_null():
    with pytest.raises(AuthException) as e:
        vt = VerifyTokenAuth(raw_token=None)
        vt.is_valid()

    assert str(e.value) == 'token not found'


def test_scopes():
    vt = VerifyTokenAuth(raw_token='', scopes_check={'foo': 'bar'})
    ut = vt.is_valid()

    assert ut.username == 'crl'


def test_scopes_raises():
    with pytest.raises(AuthException) as e:
        vt = VerifyTokenAuth(raw_token='', scopes_check={'bar': 'foo'})
        vt.is_valid()

    assert str(e.value) == 'user has not permission scopes'


def test_create_resp():
    vt = VerifyTokenAuth(raw_token='', scopes_check={'foo': 'bar'})

    res = vt.create_resp_err('error')

    assert res == {'error': 'error'}


def test_create_resp_func():
    def custom_error_resp(err: str):
        return err

    vt = VerifyTokenAuth(raw_token='',
                         scopes_check={'foo': 'bar'},
                         resp_err_fuc=custom_error_resp)

    res = vt.create_resp_err('error')

    assert res == 'error'
