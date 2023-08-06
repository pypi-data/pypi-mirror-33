import pytest

from clean.exceptions import FilterDoesNotExist, RepositoryException
from clean.repository.abs import RepoListBase
from clean.repository.list import find_all_filter, find_filters, filtering, RepoListMeta


def test_filtering_decorator():
    @filtering(name='func')
    def my_func():
        pass

    assert my_func.f_alias == 'func'


def test_filtering_decorator_with_default_dynamic():
    @filtering(name='func')
    def my_func():
        pass

    assert my_func.dynamic is True


def test_filtering_decorator_dynamic():
    @filtering(name='func', dynamic=False)
    def my_func():
        pass

    assert my_func.f_alias == 'func'
    assert my_func.dynamic is False


def test_meta_filters_dynamic():
    class Foo(metaclass=RepoListMeta):

        def all(self):
            return []

        @filtering(name='getName')
        def get_by_name(self, name):
            return [name]

        @filtering(name='getScore')
        def get_by_score(self, name, score):
            return [name, score]

        @filtering(name='getMostRelevant')
        def get_most_relevant(self):
            return []

    fil = Foo._filters

    assert 'getName_name' in fil
    assert 'getScore_namescore' in fil
    assert 'getMostRelevant' in fil


def test_meta_filters_non_dynamic():
    class Foo(metaclass=RepoListMeta):

        def all(self):
            return []

        @filtering(name='getName', dynamic=False)
        def get_by_name(self, name):
            return [name]

        @filtering(name='getMostRelevant', dynamic=False)
        def get_most_relevant(self):
            return []

    fil = Foo._filters

    assert 'getName' in fil
    assert 'getMostRelevant' in fil


def test_meta_filters_dynamic_and_non_dynamic():
    class Foo(metaclass=RepoListMeta):

        def all(self):
            return []

        @filtering(name='getName')
        def get_by_name(self, name):
            return [name]

        @filtering(name='getScore')
        def get_by_score(self, name, score):
            return [name, score]

        @filtering(name='getMostRelevant', dynamic=False)
        def get_most_relevant(self):
            return []

    fil = Foo._filters

    assert 'getName_name' in fil
    assert 'getScore_namescore' in fil
    assert 'getMostRelevant' in fil


def test_base_filter_class_for_repositories():
    class Filter(RepoListBase):

        def all(self):
            return []

        def create_factory(self, raw):
            pass

        @filtering(name='byDate', dynamic=False)
        def filter_by_name(self):
            return []

    c_filter = Filter()
    res = c_filter.execute(name='byDate', filters={})

    assert c_filter.filter_by_name() == []
    assert res == []


def test_get_func_by_filter_name():
    class Filter(RepoListBase):

        def all(self):
            return []

        def create_factory(self, raw):
            pass

        @filtering(name='byDate', dynamic=False)
        def filter_by_name(self, name):
            return [name]

    c_filter = Filter()
    func = c_filter.get_func_by_name(name='byDate')

    assert callable(func) is True


def test_raise_if_name_does_not_exist():
    class Filter(RepoListBase):

        def all(self):
            return []

        def create_factory(self, raw):
            pass

        @filtering(name='byDate')
        def filter_by_name(self, name):
            return [name]

    c_filter = Filter()

    with pytest.raises(FilterDoesNotExist) as e:
        c_filter.get_func_by_name(name='byDates')

    assert str(e.value) == 'Filter name="byDates" does not exist'


class FilterTest(RepoListBase):

    def all(self):
        return []

    def create_factory(self, raw):
        pass

    @filtering(name='getName')
    def get_by_name(self, name):
        return [name]

    @filtering(name='getScore', dynamic=False)
    def get_by_score(self, name, score):
        return [name, score]

    @filtering(name='getMostRelevant', dynamic=False)
    def get_most_relevant(self):
        return []


def test_get_func_name_with_filters():
    ft = FilterTest()
    filters = dict(name=1, desc='')

    res = ft.get_func_name('myFunc', filters)
    assert res == 'myFunc_descname'


def test_get_func_name():
    ft = FilterTest()
    filters = dict()

    res = ft.get_func_name('myFunc', filters)
    assert res == 'myFunc'


def test_get_arguments_from_func():
    test_func = FilterTest._filters['getScore']

    ft = FilterTest()
    res = ft.get_func_args(test_func).args

    assert 'name' in res
    assert 'score' in res
    assert 'self' not in res


def test_verify_arguments():
    test_func = FilterTest._filters['getScore']
    ft = FilterTest()

    args = ft.get_func_args(test_func)
    filters = dict(name='crl', score=12)
    kwargs = ft.verify_arguments(args, filters)

    assert kwargs['name'] == 'crl'
    assert kwargs['score'] == 12


def test_verify_arguments_mismatch():
    test_func = FilterTest._filters['getScore']
    ft = FilterTest()

    with pytest.raises(RepositoryException) as e:
        args = ft.get_func_args(test_func)
        filters = dict()
        ft.verify_arguments(args, filters)

    assert str(e.value) == 'Missing argument: "name"'


def test_find_filter_is_empty():
    res = find_filters({})

    assert res == {}


def test_find_filter_functions():
    def find_id(uid):
        return uid

    def find_name(name):
        return name

    def not_register_this():
        pass

    find_id.f_alias = 'findById'
    find_name.f_alias = 'findByName'
    find_name.dynamic = False

    namespace = {
        'find_id': find_id,
        'find_name': find_name,
        'not_register_this': not_register_this
    }

    filters = find_filters(namespace)

    assert filters == {
        'findById_uid': find_id,
        'findByName': find_name
    }


def test_find_all_filter_in_namespace():
    def all_f():
        pass

    namespace = {
        'all': all_f
    }

    all_func = find_all_filter(namespace=namespace, bases=())

    assert callable(all_func) is True


def test_all_filter_is_not_found_in_namespace_raises_not_implemented():
    namespace = {}

    with pytest.raises(NotImplementedError) as e:
        find_all_filter(namespace=namespace, bases=())

    assert str(e.value) == "'all' filter must be implemented"


def test_all_filter_is_in_bases():
    namespace = {}

    class Foo:

        def all(self):
            pass

    all_func = find_all_filter(namespace=namespace, bases=(Foo, ))

    assert callable(all_func)


def test_base_repository_all_raises_not_implemented_error():
    repo = RepoListBase()

    with pytest.raises(NotImplementedError):
        repo.all()


def test_base_repository_create_factory_raises_not_implemented_error():
    repo = RepoListBase()

    with pytest.raises(NotImplementedError):
        repo.create_factory({})
