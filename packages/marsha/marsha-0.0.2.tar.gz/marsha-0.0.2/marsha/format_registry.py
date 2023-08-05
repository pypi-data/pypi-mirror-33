from typing import NewType


class FormatRegistry(object):
    default_formats = {}
    default_generic_formats = {}

    @classmethod
    def set_default(self, format, type=None):
        type = type or format.model_type
        self.default_formats[type] = format

    @classmethod
    def set_generic_default(self, format, type=None):
        type = type or format.generic_type.__class__
        self.default_generic_formats[type] = format

    @classmethod
    def build_type(self, format):
        type = NewType(repr(format), format.model_type)
        type.__marsha_format__ = format
        return type

    @classmethod
    def get(self, type):
        format = getattr(type, '__marsha_format__', None)
        if format:
            return format
        format = self.default_formats.get(type, None)
        if format:
            return format
        generic_format = self.default_generic_formats.get(type.__class__, None)
        if generic_format:
            return generic_format.from_type(type)
        message = 'There is no default format for {}.'.format(type.__name__)
        raise TypeError(message)

    @classmethod
    def register_format(self, format):
        format.model_type.__marsha_format__ = format
