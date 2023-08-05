from dateutil import parser
from datetime import datetime
from .base_format import BaseFormat


# TODO: Break this out into a module named marsha_dateutil
class ISODateString(BaseFormat):
    python_type = datetime
    formatted_type = str

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def load(self, data: formatted_type) -> python_type:
        return parser.parse(data, **self.kwargs).date()

    def dump(self, data: python_type, parent=None) -> formatted_type:
        return data.isoformat()
