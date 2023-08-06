from clean.entities.error import ErrorMessage


def test_error_message():
    err = ErrorMessage(type_='NOT FOUND', message='resource not found')

    assert err.type == 'NOT FOUND'
    assert err.message == 'resource not found'
    assert str(err) == 'NOT FOUND: resource not found'


def test_error_message_eq():
    err1 = ErrorMessage(type_='NOT FOUND', message='resource not found')
    err2 = ErrorMessage(type_='NOT FOUND', message='resource not found')

    assert err1 == err2
