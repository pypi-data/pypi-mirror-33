import pytest

from clean.utils.unique import UUIDGenerator, UniqueGenerator, ShortUUIDGenerator


def test_unique_generator_raises():

    with pytest.raises(NotImplementedError):
        g = UniqueGenerator()
        g.generate()


def test_unique_uuid4():
    gen = UUIDGenerator()
    res = gen.generate()

    assert type(res) is str


def test_unique_short_uuid():
    gen = ShortUUIDGenerator()
    res = gen.generate()

    assert type(res) is str
