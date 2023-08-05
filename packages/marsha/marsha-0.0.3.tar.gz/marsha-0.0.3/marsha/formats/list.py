import typing
from ..format_registry import FormatRegistry
from .raw_format import RawFormat


class List(RawFormat):
    formatted_type = list
    model_type = list
    generic_type = typing.List
    item_format = None

    @classmethod
    def from_type(self, list_type):
        item_type = list_type.__args__[0]

        class SpecificList(self):
            item_format = FormatRegistry.get(item_type)

        return SpecificList

    @classmethod
    def validate_type(self, data):
        error = super().validate_type(data)
        if error:
            return error

    @classmethod
    def validate_content(self, data):
        errors = [
            self.item_format.validate_content(item)
            for item in data
        ]
        return [error for error in errors if error]

    @classmethod
    def load(self, data):
        error = self.validate_type(data)
        if error:
            return None, error
        result = [
            self.item_format.load(item)
            for item in data
        ]
        errors = {
            index: error
            for index, (_, error) in enumerate(result)
            if error
        }
        if errors:
            return None, errors
        data = [value for value, _ in result]
        return data, None

    @classmethod
    def dump(self, data):
        return [
            self.item_format.dump(item)
            for item in data
        ]
