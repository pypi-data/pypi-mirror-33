from clean.entities.token import UserToken


def test_user_token_obj():
    ut = UserToken(username='crl', email='admin@admin.com', avatar='', metadata={})

    assert ut.username == 'crl'
    assert ut.email == 'admin@admin.com'
    assert ut.avatar == ''
    assert ut.metadata == {}


def test_user_token_repr():
    ut = UserToken(username='crl', email='admin@admin.com', avatar='', metadata={})

    assert str(ut) == "crl: {}"


def test_user_token_repr_with_metadata():
    ut = UserToken(username='crl', email='admin@admin.com', avatar='', metadata={'foo': 'bar'})

    assert str(ut) == "crl: {'foo': 'bar'}"


def test_user_token_from_dict():
    expected = UserToken(username='crl', email='admin@admin.com', avatar='', metadata={'foo': 'bar'})
    raw = {
        'username': 'crl',
        'email': 'admin@admin.com',
        'avatar': '',
        'metadata': {
            'foo': 'bar'
        }
    }

    res = UserToken.from_dict(raw)
    assert res == expected
