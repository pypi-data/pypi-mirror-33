from inspect import isabstract, signature

from clean.request.verifier.abs import RequestVerifierAbs


def test_request_verifier_is_abstract():
    assert isabstract(RequestVerifierAbs)


def test_request_verifier_has_is_valid_method():
    ab = RequestVerifierAbs.__abstractmethods__
    sig = str(signature(RequestVerifierAbs.is_valid))

    assert ab == frozenset(['is_valid'])
    assert sig == '(self, params:Dict)'


def test_request_verifier_has_errors():
    class R(RequestVerifierAbs):

        def is_valid(self, params):
            return True

    assert hasattr(R(), 'errors')
