from typing import get_type_hints
from ..format_registry import FormatRegistry
from .base_format import BaseFormat


class Object(BaseFormat):
    model_type = object
    formatted_type = dict
    schema_class = object
    type_hints = None
    child_formats = None

    @staticmethod
    def get_model_value(data, key):
        return getattr(data, key)

    @classmethod
    def init(self):
        super().init()
        type_hints = get_type_hints(self.schema_class)
        self.child_formats = [
            (name, FormatRegistry.get(type))
            for name, type in type_hints.items()
        ]
        self.formatted_names = {
            name: format.formatted_name
            if hasattr(format, 'formatted_name')
            else name
            for name, format in self.child_formats
        }
        self.defaults = {
            name: getattr(self.schema_class, name)
            for name in type_hints
            if hasattr(self.schema_class, name)
        }

    @classmethod
    def validate_extra_error(self, data):
        return {
            key: 'This key is not expected.'
            for key in data
            if key not in self.formatted_names.values()
        }

    @classmethod
    def validate_extra(self, data):
        return self.validate_extra_error(data)

    @classmethod
    def validate_extra_ignore(self, data):
        return {}

    @classmethod
    def get_extra(self, data):
        return self.get_extra_discard(data)

    @classmethod
    def get_extra_discard(self, data):
        return {}

    @classmethod
    def get_extra_keep(self, data):
        return {
            key: value
            for key, value in data.items()
        }

    @classmethod
    def validate_type(self, data: formatted_type):
        type_error = super().validate_type(data)
        if type_error:
            return type_error
        errors = self.validate_extra(data)
        for key, format in self.child_formats:
            data_key = self.formatted_names.get(key)
            if data_key not in data and key not in self.defaults:
                error = 'This key was not found, but it is required.'
            else:
                error = None
            if error:
                errors[key] = error
        return errors

    @classmethod
    def validate_content(self, data):
        errors = {}
        for key, format in self.child_formats:
            value = self.get_model_value(data, key)
            error = format.validate_content(value)
            if error:
                errors[key] = error
        return errors or super().validate_content(data)

    @classmethod
    def load(self, data: formatted_type) -> model_type:
        errors = self.validate_type(data)
        if errors:
            return None, errors
        init_kwargs = self.get_extra(data)
        for key, format in self.child_formats:
            data_key = self.formatted_names.get(key)
            if data_key in data:
                value, error = format.load(data[data_key])
                if error:
                    errors[key] = error
                else:
                    init_kwargs[key] = value
            else:
                init_kwargs[key] = self.defaults.get(key)
        if errors:
            return None, errors
        return self.model_type(**init_kwargs), None

    @classmethod
    def dump(self, data: model_type) -> formatted_type:
        formatted_data = self.get_extra(data)
        for key, format in self.child_formats:
            value = self.get_model_value(data, key)
            key = self.formatted_names.get(key)
            formatted_data[key] = format.dump(value)
        return formatted_data

    @classmethod
    def ignore_extra(self, enabled):
        if enabled:
            self.validate_extra = self.validate_extra_ignore
        else:
            self.validate_extra = self.validate_extra_error

    @classmethod
    def keep_extra(self, enabled):
        self.ignore_extra(enabled)
        if enabled:
            self.get_extra = self.get_extra_keep
        else:
            self.get_extra = self.get_extra_discard
