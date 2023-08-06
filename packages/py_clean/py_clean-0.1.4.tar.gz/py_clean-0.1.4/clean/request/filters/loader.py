from clean.request.filters import fields
from clean.exceptions import FilterException
from .abs import BaseFilter


def load_filter(field_name: str) -> BaseFilter:
    try:
        _class = getattr(fields, field_name)
        if not issubclass(_class, BaseFilter):
            raise FilterException('load_field field_name = "{}" is not subclass of AbsField'.format(field_name))
        return _class
    except AttributeError:
        raise FilterException('filter name "{}" does not exists'.format(field_name))
