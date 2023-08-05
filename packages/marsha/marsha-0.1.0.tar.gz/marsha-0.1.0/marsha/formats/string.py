from .raw_format import RawFormat


class String(RawFormat):
    model_type = str
    formatted_type = str

    @classmethod
    def min(self, length):
        self.min_length = length

        def min_constraint(value):
            if len(value) < self.min_length:
                error = 'Expected a minimum length of {}, but found {}.'
                return error.format(self.min_length, len(value))
        self.validators.append(min_constraint)

    @classmethod
    def max(self, length):
        self.max_length = length

        def max_constraint(value):
            if len(value) > self.max_length:
                error = 'Expected a maximum length of {}, but found {}.'
                return error.format(self.max_length, len(value))
        self.validators.append(max_constraint)
