from typing import Dict

from clean.infra.schema import Draft4Validator

from clean.entities.error import ErrorMessage
from clean.request.verifier.abs import RequestVerifierAbs


class RequestVerifierSchema(RequestVerifierAbs):

    def __init__(self, schema: Dict, val_cls=Draft4Validator):
        super(RequestVerifierSchema, self).__init__()
        self.validator = val_cls(schema)

    def validate(self, definition: Dict):
        for error in self.validator.iter_errors(definition):
            path = ".".join(str(e) for e in error.path) or '.'
            self.errors.append(ErrorMessage(type_=path, message=error.message))

    def is_valid(self, params: Dict):
        self.validate(params)
        return len(self.errors) == 0
