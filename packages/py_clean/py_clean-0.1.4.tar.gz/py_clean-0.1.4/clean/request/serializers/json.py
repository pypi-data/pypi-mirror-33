import json


class ErrorMessageEncoder(json.JSONEncoder):

    def default(self, o):
        try:
            to_serialize = {
                'type': o.type,
                'message': o.message
            }
            return to_serialize
        except AttributeError:
            return super().default(o)
