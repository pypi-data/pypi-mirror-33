from clean.utils.requests import remove_none_values_from_dict, grouping


def test_remove_nones_simple_dict():
    simple = {
        'arms': 3,
        'move': 'left',
        'axis': None
    }

    output = {
        'arms': 3,
        'move': 'left',
    }

    res = remove_none_values_from_dict(simple)
    assert res == output


def test_remove_none_from_deep_dict():
    deep = {
        'name': 'hardware',
        'sensors': {
            'gps': None,
            'temp': {
                'id': '12345678',
                'value': 1000
            }
        }
    }

    output = {
        'name': 'hardware',
        'sensors': {
            'temp': {
                'id': '12345678',
                'value': 1000
            }
        }
    }

    res = remove_none_values_from_dict(deep)
    assert res == output


def test_grouping_data_with_underscores():
    data_in = {
        'name': 'my new object',
        'created__gte': '2016011600',
        'created__lte': '2018011600',
        'page__limit': 100,
        'page__offset': 0,
        'order__order': 1
    }

    data_out = {
        'name': 'my new object',
        'created': {
            'gte': '2016011600',
            'lte': '2018011600'
        },
        'page': {
            'limit': 100,
            'offset': 0
        },
        'order': {
            'order': 1
        }
    }

    res = grouping(data_in)
    assert res == data_out
