import json

from clean.entities.error import ErrorMessage
from clean.request.serializers.json import ErrorMessageEncoder


def test_definition_encoder():
    raw = {
        'type': 'SYSTEM_ERROR',
        'message': 'some error'
    }

    res = """{"type": "SYSTEM_ERROR", "message": "some error"}"""
    definition = ErrorMessage.from_dict(raw)
    data = json.dumps(definition, cls=ErrorMessageEncoder)

    assert data == res
