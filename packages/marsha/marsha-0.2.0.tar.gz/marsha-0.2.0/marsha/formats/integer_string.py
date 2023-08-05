from .base_format import BaseFormat


class IntegerString(BaseFormat):
    model_type = int
    formatted_type = str
