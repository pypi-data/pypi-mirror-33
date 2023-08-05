from .raw_format import RawFormat


class Any(RawFormat):
    @classmethod
    def validate_type(self, data):
        pass
