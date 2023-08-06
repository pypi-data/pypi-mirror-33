from unittest import mock
from inspect import isabstract

from clean.request.inout.ports import Request
from clean.entities.error import ErrorMessage
from clean.use_case.case import UseCaseAbs


class UseCaseAbsImpl(UseCaseAbs):
    def process_request(self, req):
        return True


def test_abs_is_abstract_class():
    assert isabstract(UseCaseAbs)


def test_abs_use_case_invalid_request():
    invalid_request = Request()
    invalid_request.add_error(ErrorMessage('someParam', 'some message'))

    use_case = UseCaseAbsImpl()
    res = use_case.execute(invalid_request)

    assert bool(res) is False


def test_use_case_exception_from_process_request():
    use_case = UseCaseAbsImpl()

    class TestException(Exception):
        pass

    use_case.process_request = mock.Mock()
    use_case.process_request.side_effect = TestException('some message')
    res = use_case.execute(mock.Mock)

    assert bool(res) is False
    assert len(res.errors) == 1
    assert res.errors[0].message == 'TestException: some message'


def test_log_error_in_invalid_request():
    logger = mock.Mock()

    class FooCase(UseCaseAbs):
        def process_request(self, req):
            return True

        def logger(self):
            return logger

    invalid_request = Request()
    invalid_request.add_error(ErrorMessage('someParam', 'some message'))

    use_case = FooCase()
    res = use_case.execute(invalid_request)

    assert bool(res) is False
    assert logger.debug.call_count == 1


def test_log_an_exception_from_process_request():
    logger = mock.Mock()

    class TestException(Exception):
        pass

    class FooCase(UseCaseAbs):
        def process_request(self, req):
            return True

        def logger(self):
            return logger

    use_case = FooCase()

    use_case.process_request = mock.Mock()
    use_case.process_request.side_effect = TestException('some message')
    res = use_case.execute(mock.Mock)

    assert bool(res) is False
    assert len(res.errors) == 1
    assert logger.exception.call_count == 1


def test_log_hide_error_resp():
    logger = mock.Mock()

    class TestException(Exception):
        pass

    class FooCase(UseCaseAbs):
        def process_request(self, req):
            return True

        def logger(self):
            return logger

        def show_error(self):
            return False

    use_case = FooCase()

    use_case.process_request = mock.Mock()
    use_case.process_request.side_effect = TestException('some message')
    res = use_case.execute(mock.Mock)

    assert bool(res) is False
    assert len(res.errors) == 1
    assert logger.exception.call_count == 1
    assert res.errors[0].message == "Server Error, We're working to solve this issue."
