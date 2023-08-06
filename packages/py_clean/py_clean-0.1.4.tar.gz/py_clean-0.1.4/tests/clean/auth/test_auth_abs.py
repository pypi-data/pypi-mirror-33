from inspect import isabstract, signature

from clean.auth.abs import DecodeToken


def test_factory_abs_is_abstract_class():
    assert isabstract(DecodeToken)


def test_factory_abs_has_create_method_as_abstract():
    ab = DecodeToken.__abstractmethods__
    verify_sig = str(signature(DecodeToken.verify))

    assert ab == frozenset(['verify'])
    assert verify_sig == '(self, token:str)'
