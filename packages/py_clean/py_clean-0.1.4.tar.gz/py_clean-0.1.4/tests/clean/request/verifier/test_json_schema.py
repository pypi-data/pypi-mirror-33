from clean.request.verifier.json_schema import RequestVerifierSchema


def test_request_verifier_schema_invalid():
    sch = {
        'type': 'object',
        'properties': {
            'title': {
                'type': 'string'
            },
        },
        'required': ['type'],
        'additionalProperties': False
    }
    req = RequestVerifierSchema(sch)

    assert req.is_valid({'type': 1}) is False
    assert len(req.errors) == 1
    assert req.errors[0].type == '.'
    assert req.errors[0].message == "Additional properties are not allowed ('type' was unexpected)"


def test_request_verifier_schema_valid():
    sch = {
        'type': 'object',
        'properties': {
            'title': {
                'type': 'string'
            },
        },
        'required': ['title'],
        'additionalProperties': False
    }
    req = RequestVerifierSchema(sch)

    assert req.is_valid({'title': '2'}) is True
    assert len(req.errors) == 0
