import pytest

from clean.request.filters.fields.string import StringFilter
from clean.request.filters.loader import load_filter
from clean.exceptions import FilterException


def test_load_field_raises_if_does_not_exists():
    with pytest.raises(FilterException) as e:
        load_filter('')
    assert str(e.value) == 'filter name "" does not exists'


def test_load_field_valid():
    cf = load_filter('StringFilter')
    assert cf is StringFilter
