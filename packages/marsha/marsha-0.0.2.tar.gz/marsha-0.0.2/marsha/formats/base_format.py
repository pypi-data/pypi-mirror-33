from .raw_format import RawFormat


class BaseFormat(RawFormat):
    @classmethod
    def load(self, data):
        error = self.validate_type(data)
        if error:
            return None, error
        return self.model_type(data), None

    @classmethod
    def dump(self, data):
        return self.formatted_type(data)
