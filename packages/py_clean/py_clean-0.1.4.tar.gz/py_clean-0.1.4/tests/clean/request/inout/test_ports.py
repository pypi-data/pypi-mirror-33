import pytest

from clean.entities import resp_status
from clean.entities.error import ErrorMessage
from clean.request.inout.ports import Request, Response, ResponseFailureBuilder


def test_request_is_valid():
    req = Request()

    assert bool(req) is True


def test_request_is_not_valid():
    req = Request()
    req.add_error(ErrorMessage('field.name', 'mandatory field'))

    assert bool(req) is False


def test_request_add_error():
    req = Request()

    req.add_error(ErrorMessage('field.name', 'mandatory field'))

    assert bool(req) is False
    assert len(req.errors) == 1
    assert req.errors[0].type == 'field.name'
    assert req.errors[0].message == 'mandatory field'


def test_request_multiple_errors():
    req = Request()

    req.add_errors([ErrorMessage('field.name', 'mandatory field')])

    assert bool(req) is False
    assert len(req.errors) == 1
    assert req.errors[0].type == 'field.name'
    assert req.errors[0].message == 'mandatory field'


def test_response_is_success():
    res = Response()

    assert bool(res) is True


def test_success_response_is_true_with_context():
    res = Response(context='OK')

    assert bool(res) is True


def test_response_success_contains_result():
    res = 'OK'
    response = Response(res)

    assert response.result == res


def test_response_failure_has_errors():
    res_type = 'Context Error'
    res_message = 'This is an error'
    res_error_type = 'Error Type'
    response = Response(status=res_error_type)
    response.add_error(ErrorMessage(res_type, res_message))

    assert bool(response) is False
    assert len(response.errors) == 1
    assert response.status == res_error_type
    assert response.errors[0].type == res_type
    assert response.errors[0].message == res_message


def test_response_can_add_multiples_errors():
    res_type = 'Context Error'
    res_message = 'This is an error'
    response = Response()
    response.add_errors([ErrorMessage(res_type, res_message)])

    assert bool(response) is False
    assert len(response.errors) == 1
    assert response.errors[0].type == res_type
    assert response.errors[0].message == res_message


def test_response_build_resource_error():
    response = ResponseFailureBuilder.build_resource_error("test message")

    assert bool(response) is False
    assert response.errors[0].type == resp_status.RESOURCE_ERROR
    assert response.errors[0].message == "test message"


def test_response_builder_system_error():
    response = ResponseFailureBuilder.build_system_error("test message")

    assert bool(response) is False
    assert response.errors[0].type == resp_status.SYSTEM_ERROR
    assert response.errors[0].message == "test message"


def test_response_builder_from_invalid_request():
    invalid_req = Request()
    invalid_req.add_error(ErrorMessage(type_='name', message='exceed max chars'))
    invalid_req.add_error(ErrorMessage(type_='age', message='is not integer'))

    response = ResponseFailureBuilder.build_from_invalid_request(invalid_req)

    assert bool(response) is False
    assert response.status == resp_status.PARAMETERS_ERROR
    assert len(response.errors) == 2
    assert response.errors[0].type == 'name'
    assert response.errors[0].message == 'exceed max chars'
    assert response.errors[1].type == 'age'
    assert response.errors[1].message == 'is not integer'


def test_request_must_implement_from_dict():
    req = Request()

    with pytest.raises(NotImplementedError):
        req.from_dict({})
