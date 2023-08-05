from datetime import datetime
from .base_format import BaseFormat


class DateString(BaseFormat):
    model_type = datetime
    formatted_type = str
    formatted_encoding = None

    @classmethod
    def encoding(self, encoding: str):
        self.formatted_encoding = encoding

    @classmethod
    def load(self, data: formatted_type) -> model_type:
        error = self.validate_type(data)
        if error:
            return None, error
        try:
            return datetime.strptime(data, self.formatted_encoding), None
        except ValueError:
            error = 'Expected the encoding to be {}, but found {}.'.format(
                self.formatted_encoding,
                data,
            )
            return None, error

    @classmethod
    def dump(self, data: model_type) -> formatted_type:
        return data.strftime(self.formatted_encoding)
