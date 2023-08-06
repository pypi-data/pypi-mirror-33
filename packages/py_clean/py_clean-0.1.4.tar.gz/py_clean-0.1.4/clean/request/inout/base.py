import collections
import copy
import abc
from typing import Dict

from clean.request.verifier.json_schema import RequestVerifierSchema
from clean.request.filters.loader import load_filter
from clean.request.inout.filter import Page, Sort
from clean.request.inout.ports import Request
from clean.exceptions import FilterException


ROOT = {
    'type': 'object',
    'properties': {},
    'additionalProperties': False
}


FIELDS = {
    'fields': {
        'dateRange': {
            'type': 'object',
            'properties': {
                'gte': {'type': 'string'},
                'lte': {'type': 'string'},
            },
            'additionalProperties': False
        },
        'string': {
            'type': 'object',
            'properties': {
                'type': {'type': 'string', 'enum': ['re', 'in', 'eq', 'nq']},
                'value': {'type': 'string'}
            },
            'additionalProperties': False
        }
    }
}


FILTERS = {
    'page': {
        'type': 'object',
        'properties': {
            'offset': {'type': 'integer', 'minimum': 0},
            'limit': {'type': 'integer', 'minimum': 0}
        },
        'additionalProperties': False
    },
    'sort': {
        'type': 'object',
        'properties': {
            'by': {'type': 'string'}
        },
        'additionalProperties': False
    }
}


def update(dst: Dict, src: Dict):
    for k, v in src.items():
        if isinstance(v, collections.Mapping):
            dst[k] = update(dst.get(k, {}), v)
        else:
            dst[k] = v
    return dst


def create_filter_instances(properties: Dict, params: Dict):
    kwargs = dict()
    for k, v in properties.items():
        if '@filter' in v:
            name = v['@filter']
            _cls = load_filter(name)
            value = _cls.from_dict(params.get(k, {}), v.get('@default', {}))
            if value.is_valid():
                kwargs[k] = value
        else:
            val = params.get(k, v.get('@default'))
            if val is not None:
                kwargs[k] = val
    return kwargs


def create_page(params):
    return Page.from_dict(params)


def create_sort(params):
    return Sort.from_dict(params)


class BaseMetaIn(abc.ABCMeta, type):

    def __new__(mcs, name, bases, namespace):
        schema = namespace.get('SCHEMA', {})
        sch = copy.deepcopy(ROOT)
        sch = update(sch, schema)
        namespace['SCHEMA'] = sch
        namespace['_SCHEMA'] = schema
        return super(BaseMetaIn, mcs).__new__(mcs, name, bases, namespace)


class BaseListMetaIn(abc.ABCMeta, type):

    def __new__(mcs, name, bases, namespace):
        schema = namespace.get('SCHEMA', {})
        max_limit = namespace.get('LIMIT', 1000)
        sch = copy.deepcopy(ROOT)
        filters = copy.deepcopy(FILTERS)
        filters['page']['properties']['limit']['maximum'] = max_limit
        sch.update(FIELDS)
        sch['properties'] = filters
        sch = update(sch, schema)
        fields = namespace.get('FIELDS', [])
        if len(fields) == 0 and 'properties' in schema and type(schema['properties']) is dict:
            for key in schema['properties'].keys():
                fields.append(key)
        namespace['FIELDS'] = fields
        namespace['SCHEMA'] = sch
        namespace['_SCHEMA'] = schema
        return super(BaseListMetaIn, mcs).__new__(mcs, name, bases, namespace)


class BaseInput(Request, metaclass=BaseMetaIn):
    SCHEMA = {}
    FIELDS = []
    SCHEMA_VERIFIER_CLS = RequestVerifierSchema

    @abc.abstractclassmethod
    def from_dict(cls, params: Dict) -> Request:
        """"""

    @classmethod
    def factory(cls, params: Dict) -> Request:
        return cls.create_instance(params)

    @classmethod
    def create_instance(cls, params: Dict):
        properties = cls.SCHEMA.get('properties', {})
        kwargs = dict()
        for k, v in properties.items():
            if k not in params:
                if '@default' in v:
                    kwargs[k] = v['@default']
                else:
                    FilterException('missing argument: "{}"'.format(k))
            else:
                kwargs[k] = params[k]
        try:
            return cls(**kwargs)
        except TypeError:
            raise FilterException('missing arguments')


class BaseFilterInput(Request, metaclass=BaseListMetaIn):
    SCHEMA = {}
    FIELDS = []
    LIMIT = 1000
    DEFAULT = True
    SCHEMA_VERIFIER_CLS = RequestVerifierSchema

    def __init__(self, ft='all', page: Page=None, sort: Sort=None):
        super(BaseFilterInput, self).__init__()
        self._page = page if page is not None else Page()
        self._sort = sort if sort is not None else Sort()
        self.ft = ft

    @abc.abstractclassmethod
    def from_dict(cls, params: Dict):
        """"""

    @classmethod
    def factory(cls, params: Dict):
        return cls.create_instance(params)

    @property
    def page(self):
        return {
            'offset': self._page.offset,
            'limit': self._page.limit
        }

    @property
    def sort(self):
        return {
            'by': self._sort.by
        }

    @property
    def filters(self):
        res = dict()
        for key in self.FIELDS:
            if getattr(self, key):
                value = getattr(self, key)
                if hasattr(value, 'to_dict'):
                    res[key] = value.to_dict()
                else:
                    res[key] = value
        return res

    @classmethod
    def create_instance(cls, params: Dict):
        properties = cls.SCHEMA.get('properties', {})
        kwargs = cls.prepare_filters(params)

        filters = create_filter_instances(properties, params)
        kwargs.update(filters)
        try:
            return cls(**kwargs)
        except TypeError:
            raise FilterException('missing arguments')

    @classmethod
    def prepare_filters(cls, params):
        kwargs = dict()
        kwargs['ft'] = params.pop('ft', 'all')
        kwargs['sort'] = create_sort(params.pop('sort', {}))
        kwargs['page'] = create_page(params.pop('page', {}))
        return kwargs
