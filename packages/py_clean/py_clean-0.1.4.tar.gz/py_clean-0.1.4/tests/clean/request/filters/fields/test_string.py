from clean.request.filters.fields.string import StringFilter


def test_string_filter():
    desc = StringFilter(value='id=1', type_='nq')

    assert desc.value == 'id=1'
    assert desc.type == 'nq'


def test_string_filter_from_dict():
    params = dict(value='id=1', type='eq')
    desc = StringFilter.from_dict(params)

    assert desc.value == 'id=1'
    assert desc.type == 'eq'


def test_string_filter_to_dict():
    desc = StringFilter(value='id=1', type_='in')

    assert desc.to_dict()['value'] == 'id=1'
    assert desc.to_dict()['type'] == 'in'


def test_string_is_valid():
    desc = StringFilter(value='some value')

    assert desc.is_valid() is True


def test_string_is_invalid():
    desc = StringFilter(value='')

    assert desc.is_valid() is False
