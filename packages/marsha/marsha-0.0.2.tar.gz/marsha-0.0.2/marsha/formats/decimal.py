import decimal
from .base_format import BaseFormat


class Decimal(BaseFormat):
    model_type = decimal.Decimal
    formatted_type = decimal.Decimal
