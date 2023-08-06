import copy
import pytest
import datetime

from clean.request.inout.base import BaseMetaIn, BaseInput, BaseListMetaIn, BaseFilterInput
from clean.request.inout.base import update, create_page, create_sort, create_filter_instances
from clean.request.filters.fields import DateFilter
from clean.exceptions import FilterException

from .templates import ROOT, FIELDS, FILTERS


def test_deep_dictionary_update():
    a = {
        'b': True,
        'c': {
            'x': {
                'res': ['items'],
                'z': 1
            }
        }
    }

    b = {
        'c': {
            'new_key': 'my_field',
            'x': {
                'res': ['new items']
            }
        }
    }

    merged = {
        'b': True,
        'c': {
            'new_key': 'my_field',
            'x': {
                'res': ['new items'],
                'z': 1
            }
        }
    }

    res = update(a, b)
    assert res == merged


def test_base_meta_in():

    class Foo(metaclass=BaseMetaIn):
        pass

    assert Foo.SCHEMA == ROOT
    assert Foo._SCHEMA == {}


def test_base_request_required_from_dict():

    with pytest.raises(TypeError) as e:
        class Foo(BaseInput):
            @classmethod
            def factory(cls, params):
                pass
        Foo()
    assert str(e.value) == "Can't instantiate abstract class Foo with abstract methods from_dict"


def test_base_list_meta_in():
    class Foo(metaclass=BaseListMetaIn):
        pass

    root = copy.deepcopy(ROOT)
    fields = copy.deepcopy(FIELDS)
    filters = copy.deepcopy(FILTERS)
    root.update(fields)
    root['properties'] = filters

    assert Foo.SCHEMA == root
    assert Foo._SCHEMA == {}


class FooBar(BaseFilterInput):
    SCHEMA = {
        'properties': {
            'name': {'type': 'string'},
        }
    }
    FIELDS = ['name']

    def __init__(self, name, **kwargs):
        super(FooBar, self).__init__(**kwargs)
        self.name = name

    @classmethod
    def from_dict(cls, params):
        return cls.factory(params)

    @classmethod
    def factory(cls, params):
        return cls(name=params['name'])


def test_base_list_filter_page():
    blf = FooBar.from_dict(dict(name="test"))

    assert blf.page == {'offset': 0, 'limit': 100}


def test_base_list_filter_sort():
    blf = FooBar.from_dict(dict(name="test"))

    assert blf.sort == {'by': ''}


def test_base_list_request_required_from_dict():

    with pytest.raises(TypeError) as e:
        class Foo(BaseFilterInput):
            @classmethod
            def factory(cls, params):
                pass
        Foo()
    assert str(e.value) == "Can't instantiate abstract class Foo with abstract methods from_dict"


def test_base_list_filter_assert_validation():
    my_filter = FooBar.from_dict({'name': '1'})

    assert bool(my_filter) is True
    assert my_filter.filters == {'name': '1'}
    assert my_filter.page == {'offset': 0, 'limit': 100}
    assert my_filter.sort == {'by': ''}
    assert my_filter.ft == 'all'


def test_base_list_in_from_dict():
    my_filter = FooBar.from_dict({'name': '1'})

    assert my_filter.filters == {'name': '1'}


def test_base_class_object_input_has_to_dict_method():
    class Foo:

        def to_dict(self):
            return {
                'age': 20,
                'name': 'crl'
            }

    class Baz(BaseFilterInput):
        SCHEMA = {
            'properties': {
                'foo': {'type': 'object'}
            }
        }

        def __init__(self, foo: Foo):
            super(Baz, self).__init__()
            self.foo = foo

        @classmethod
        def from_dict(cls, params):
            return cls.factory(params)

        @classmethod
        def factory(cls, params):
            return cls(Foo())

    baz = Baz.from_dict({})
    res = baz.filters

    assert res == {'foo': {'age': 20, 'name': 'crl'}}


def test_create_page():
    params = dict(offset=100, limit=1000)
    page = create_page(params)

    assert page.limit == 1000
    assert page.offset == 100


def test_create_sort():
    params = dict(by='created')
    sort = create_sort(params)

    assert sort.by == 'created'


def test_create_filters():
    params = {
        'created': {
            'gte': '20170102000000',
            'lte': '20180102000000',
        }
    }
    properties = {
        'created': {'@filter': 'DateFilter'}
    }
    filters = create_filter_instances(properties, params)

    assert isinstance(filters['created'], DateFilter)


def test_create_filters_with_defaults():
    params = {
    }
    properties = {
        'created': {'@filter': 'DateFilter', '@default': {'gte': '20170102000000', 'lte': '20180102000000'}}
    }
    filters = create_filter_instances(properties, params)

    assert isinstance(filters['created'], DateFilter)


def test_create_filters_raise_error():
    params = {
        'created': {
            'gte': '20170102000000',
            'lte': '20180102000000',
        }
    }
    properties = {
        'created': {'@filter': 'DateTimeFilter'}
    }

    with pytest.raises(FilterException):
        create_filter_instances(properties, params)


def test_base_filter_create_instance_class_dynamically():
    class BazFilter(BaseFilterInput):
        SCHEMA = {
            'properties': {
                'uid': {'type': 'string'},
                'created': {'$ref': '#/fields/dateRange', '@filter': 'DateFilter'},
            }
        }

        def __init__(self, uid=None, created=None, **kwargs):
            super(BazFilter, self).__init__(**kwargs)
            self.uid = uid
            self.created = created

        @classmethod
        def from_dict(cls, kwargs):
            return kwargs

    params = {
        'created': {
            'gte': '20170102000000',
            'lte': '20180102000000',
        },
        'page': {
            'offset': 1000
        },
        'uid': '123'
    }
    instance = BazFilter.create_instance(params=params)

    assert instance.uid == '123'
    assert instance.page['offset'] == 1000
    assert isinstance(instance.created.gte, datetime.datetime)


def test_base_filter_create_instance_class_dynamically_raise_missing_arguments():
    class BazFilter(BaseFilterInput):
        SCHEMA = {
            'properties': {
                'uid': {'type': 'string'},
            }
        }

        def __init__(self, uid, created, **kwargs):
            super(BazFilter, self).__init__(**kwargs)
            self.uid = uid
            self.created = created

        @classmethod
        def from_dict(cls, kwargs):
            return kwargs

    params = {
        'created': {
            'gte': '20170102000000',
            'lte': '20180102000000',
        },
        'uid': '123'
    }

    with pytest.raises(FilterException):
        BazFilter.create_instance(params=params)


def test_base_create_instance_class_dynamically_with_defaults():
    class BazFilter(BaseInput):
        SCHEMA = {
            'properties': {
                'uid': {'type': 'string', '@default': '123'},
            }
        }

        def __init__(self, uid=None, created=None):
            super(BazFilter, self).__init__()
            self.uid = uid
            self.created = created

        @classmethod
        def from_dict(cls, kwargs):
            return kwargs

    params = {}
    instance = BazFilter.create_instance(params=params)

    assert instance.uid == '123'


def test_base_create_instance_class_dynamically_raise_missing_arguments():
    class BazFilter(BaseInput):
        SCHEMA = {
            'properties': {
                'uid': {'type': 'string'},
            }
        }

        def __init__(self, uid, created, **kwargs):
            super(BazFilter, self).__init__(**kwargs)
            self.uid = uid
            self.created = created

        @classmethod
        def from_dict(cls, kwargs):
            return kwargs

    params = {
        'created': {
            'gte': '20170102000000',
            'lte': '20180102000000',
        },
        'uid': '123'
    }

    with pytest.raises(FilterException):
        BazFilter.create_instance(params=params)
