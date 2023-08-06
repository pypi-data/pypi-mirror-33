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
            'limit': {'type': 'integer', 'minimum': 0, 'maximum': 1000}
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
