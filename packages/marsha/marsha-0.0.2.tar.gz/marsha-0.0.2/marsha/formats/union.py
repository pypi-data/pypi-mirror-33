import typing
from ..format_registry import FormatRegistry
from .raw_format import RawFormat


class Union(RawFormat):
    generic_type = typing.Union

    @classmethod
    def from_type(self, union_type):
        class SpecificUnion(self):
            formatted_type = union_type
            model_type = union_type

        return SpecificUnion

    @classmethod
    def get_format(self, data):
        for type in self.formatted_type.__args__:
            format = FormatRegistry.get(type)
            error = format.validate_type(data)
            if not error:
                return format

    @classmethod
    def get_type_names(self):
        type_names = [
            type.__name__
            for type in self.formatted_type.__args__
        ]
        return ' or '.join(type_names)

    @classmethod
    def get_format_from_model_data(self, data):
        for type in self.formatted_type.__args__:
            format = FormatRegistry.get(type)
            if isinstance(data, format.model_type):
                return format
        message = 'Expected {}, but found {}.'.format(
            self.get_type_names(),
            data.__class__.__name__,
        )
        raise TypeError(message)

    @classmethod
    def load(self, data):
        format = self.get_format(data)
        if not format:
            error = 'Expected {}, but found {}.'.format(
                self.get_type_names(),
                data.__class__.__name__,
            )
            return None, error
        return format.load(data)

    @classmethod
    def dump(self, data):
        format = self.get_format_from_model_data(data)
        return format.dump(data)
