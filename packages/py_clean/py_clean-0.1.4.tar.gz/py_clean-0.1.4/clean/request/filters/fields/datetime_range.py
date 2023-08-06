import pytz
from typing import Dict
from datetime import datetime

from clean.exceptions import FilterException
from clean.request.filters.abs import BaseFilter


class DateFilter(BaseFilter):
    def __init__(self, gte: str='', lte: str='', fmt="%Y%m%d%H%M%S"):
        self.fmt = fmt
        self.gte = self.to_datetime(gte, "gte") if gte else gte
        self.lte = self.to_datetime(lte, "lte") if lte else lte

    def to_datetime(self, date_string, arg_name):
        try:
            return datetime.strptime(date_string, self.fmt).replace(tzinfo=pytz.UTC)
        except ValueError:
            raise FilterException('"DateFilter": arg="{}" time data \'{}\' '
                                  'does not match format \'%Y%m%d%H%M%S\''.format(arg_name, date_string))

    @classmethod
    def from_dict(cls, params: Dict, defaults: Dict=None):
        defaults = defaults if defaults is not None else {}
        return cls(gte=params.get('gte', defaults.get('gte')),
                   lte=params.get('lte', defaults.get('lte')),
                   fmt=params.get('fmt', "%Y%m%d%H%M%S"))

    def to_dict(self):
        return {
            'gte': self.gte,
            'lte': self.lte,
        }

    def is_valid(self):
        return self.gte is not None and self.lte is not None \
               and self.gte != '' and self.lte != ''
