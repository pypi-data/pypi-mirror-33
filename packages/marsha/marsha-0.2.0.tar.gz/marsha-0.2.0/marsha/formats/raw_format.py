from typing import Any


class RawFormat(object):
    model_type = Any
    formatted_type = Any
    validators = ()

    @classmethod
    def init(self):
        self.validators = []

    @classmethod
    def validate_type(self, data: formatted_type):
        if not isinstance(data, self.formatted_type):
            error = 'Expected {}, but found {}.'
            return error.format(
                self.formatted_type.__name__,
                data.__class__.__name__,
            )

    @classmethod
    def load(self, data: formatted_type) -> model_type:
        error = self.validate_type(data)
        if error:
            return None, error
        return data, None

    @staticmethod
    def dump(data: model_type) -> formatted_type:
        return data

    @classmethod
    def validate_content(self, data):
        for validator in self.validators:
            error = validator(data)
            if error:
                return error

    @classmethod
    def add_validator(self, validator):
        self.validators.append(validator)

    @classmethod
    def add_constraints(self, constraints, name=None):
        for constraint, option in constraints.items():
            if hasattr(self, constraint):
                getattr(self, constraint)(option)
            else:
                message = 'The {} format has no constraint named {}.'
                name = name or self.__name__
                raise AttributeError(message.format(name, constraint))

    @classmethod
    def map(self, name):
        """
        Instructs a schema to use an alternate name when reading during a load
        or writing during a dump.

        Arguments:
            name (str): The key the value uses in a schema's serialized state.
        """
        self.formatted_name = name

    @classmethod
    def compile(self, enabled):
        loc = {}
        context = {'id': 0}
        compile_dump = self.compile_dump('data', context)
        inline_dump = 'def dump(data):\n return {}\n'.format(compile_dump)
        exec(inline_dump, globals(), loc)
        self.dump = loc['dump']

    @staticmethod
    def compile_dump(scope, context):
        return scope
