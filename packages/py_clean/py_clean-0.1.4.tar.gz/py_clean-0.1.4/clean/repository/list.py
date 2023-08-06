import inspect
from typing import Dict, Iterator

from clean.exceptions import FilterDoesNotExist
from clean.exceptions import RepositoryException


def filtering(name: str, dynamic: bool=True):
    def wrap(f):
        f.f_alias = name
        f.dynamic = dynamic
        return f
    return wrap


def find_filters(namespace: Dict):
    filters = {}
    for f_name in namespace.keys():
        func = namespace.get(f_name)
        f_alias = getattr(func, 'f_alias', None)
        dynamic = getattr(func, 'dynamic', True)
        if f_alias:
            if dynamic:
                args = inspect.getfullargspec(func).args
                if args and args[0] == 'self':
                    args = args[1:]
                args = "".join(sorted(args))
                if args:
                    f_alias = "{}_{}".format(f_alias, args)
                filters[f_alias] = func
            else:
                filters[f_alias] = func
    return filters


def find_all_filter(namespace: Dict, bases: Iterator):
    if 'all' in namespace:
        return namespace.get('all')
    else:
        for base in bases:
            if hasattr(base, 'all'):
                return getattr(base, 'all')
        raise NotImplementedError("'all' filter must be implemented")


class RepoListMeta(type):
    def __new__(mcs, name, bases, namespace):
        filters = namespace['_filters'] = find_filters(namespace)
        filters['all'] = find_all_filter(namespace, bases)
        return super(RepoListMeta, mcs).__new__(mcs, name, bases, namespace)


class RepoListBase(metaclass=RepoListMeta):

    def all(self):
        raise NotImplementedError

    def execute(self, name: str, filters: Dict=None, page: Dict=None, sort: Dict=None):
        filters = filters if filters else dict()
        page = page if page else dict(offset=0, limit=100)
        sort = sort if sort else dict(by='')

        filter_name = self.get_func_name(name, filters)
        query_func = self.get_func_by_name(filter_name)
        arguments = self.get_func_args(query_func)

        kwargs = self.verify_arguments(arguments, filters)
        qs = query_func(self, **kwargs)

        results = self.limit_results(qs, page, sort)
        return self.to_entities(results)

    @staticmethod
    def get_func_name(name: str, filters: Dict):
        filters_name = "".join(sorted(filters.keys()))
        if filters_name:
            return "{}_{}".format(name, filters_name)
        return name

    @staticmethod
    def get_simple_name(name: str):
        return name.split('_')[0]

    def get_func_by_name(self, name):
        if name not in self._filters:
            name = self.get_simple_name(name)
            if name not in self._filters:
                raise FilterDoesNotExist('Filter name="{}" does not exist'.format(name))
        return self._filters[name]

    @staticmethod
    def get_func_args(filter_func):
        assert callable(filter_func), 'filter func is not callable'
        arguments = inspect.getfullargspec(filter_func)
        if 'self' in arguments.args:
            arguments.args.remove('self')
        return arguments

    @staticmethod
    def verify_arguments(arguments, filters: Dict):
        kwargs = dict()
        for key in arguments.args:
            if key not in filters:
                raise RepositoryException('Missing argument: "{}"'.format(key))
            kwargs[key] = filters[key]
        return kwargs

    def limit_results(self, qs: Iterator, page: Dict, sort: Dict):
        qs = self.limit(qs, page)
        qs = self.sort(qs, sort)
        return qs

    def limit(self, qs: Iterator, page: Dict):
        return qs

    def sort(self, qs: Iterator, sort: Dict):
        return qs

    def to_entities(self, results: Iterator):
        return [self.create_factory(raw=ele) for ele in results]

    def create_factory(self, raw: Dict):
        raise NotImplementedError
