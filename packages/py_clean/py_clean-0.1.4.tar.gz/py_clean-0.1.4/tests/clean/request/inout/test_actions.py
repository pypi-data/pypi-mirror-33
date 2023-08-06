from clean.request.filters.fields import DateFilter
from clean.request.inout.actions import RetrieveRequest, DeleteRequest, BaseRequest, ListRequest


class FooBase(BaseRequest):
    SCHEMA = {
        'properties': {
            'name': {'type': 'string'},
            'last': {'type': 'string'},
            'age': {'type': 'number', '@default': 0}
        },
        'required': ['name']
    }
    FIELDS = ['name', 'last']

    def __init__(self, name, age, last=""):
        super(FooBase, self).__init__()
        self.name = name
        self.last = last
        self.age = age


class FooList(ListRequest):
    SCHEMA = {
        'properties': {
            'name': {'type': 'string'},
            'last': {'type': 'string'},
            'created': {'$ref': '#/fields/dateRange'}
        },
        'required': ['name']
    }
    FIELDS = ['name', 'last']

    def __init__(self, name, created: DateFilter, last=""):
        super(FooList, self).__init__()
        self.name = name
        self.created = created
        self.last = last

    @classmethod
    def factory(cls, params) -> 'FooList':
        return cls(name=params['name'],
                   last=params.get('last'),
                   created=DateFilter.from_dict(params.get('created', {})))


def test_base_list_request():
    res = FooList.from_dict({'name': 'crl', 'last': 'rl'})
    assert bool(res) is True
    assert res.filters == {'name': 'crl', 'last': 'rl'}
    assert res.page == {'offset': 0, 'limit': 100}


def test_base_list_request_throw_an_error():
    res = FooList.from_dict({'name': 'crl', 'last': 'rl', 'created__lte': '2000'})

    assert bool(res) is False
    assert len(res.errors) == 1


def test_retrieve_is_valid():
    req = RetrieveRequest.from_dict({'oid': '123311'})

    assert bool(req) is True


def test_retrieve_oid_is_not_an_string():
    req = RetrieveRequest.from_dict({'oid': 123311})

    assert bool(req) is False
    assert len(req.errors) == 1


def test_delete_is_valid():
    req = DeleteRequest.from_dict({'oid': '123311'})

    assert bool(req) is True


def test_delete_oid_is_not_an_string():
    req = DeleteRequest.from_dict({'oid': 123311})

    assert bool(req) is False
    assert len(req.errors) == 1
