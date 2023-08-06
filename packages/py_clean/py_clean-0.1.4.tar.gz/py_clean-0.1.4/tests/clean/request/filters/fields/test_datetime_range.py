import pytest
import pytz
from datetime import datetime

from clean.exceptions import FilterException
from clean.request.filters.fields.datetime_range import DateFilter


def test_date_filter():
    created = DateFilter(gte='20160101000000', lte='20170101235959')

    assert created.gte == datetime(2016, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)
    assert created.lte == datetime(2017, 1, 1, 23, 59, 59, tzinfo=pytz.UTC)


def test_date_filter_from_dict():
    params = dict(gte='20160101000000', lte='20170101235959')
    created = DateFilter.from_dict(params)

    assert created.gte == datetime(2016, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)
    assert created.lte == datetime(2017, 1, 1, 23, 59, 59, tzinfo=pytz.UTC)


def test_date_filter_to_dict():
    created = DateFilter(gte='20160101000000', lte='20170101235959')

    assert created.to_dict()['gte'] == datetime(2016, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)
    assert created.to_dict()['lte'] == datetime(2017, 1, 1, 23, 59, 59, tzinfo=pytz.UTC)


def test_date_filter_raising():

    with pytest.raises(FilterException) as f:
        DateFilter(gte='20160101000000', lte='20170101')

    assert str(f.value) == '"DateFilter": arg="lte" time data \'20170101\' does not match format \'%Y%m%d%H%M%S\''


def test_date_filter_is_valid():
    created = DateFilter(gte='20160101000000', lte='20170101235959')

    assert created.is_valid() is True


def test_date_filter_is_invalid():
    created = DateFilter(gte='20160101000000')

    assert created.is_valid() is False
