from .object import Object


class Dict(Object):
    model_type = dict
    formatted_type = dict
    schema_class = object

    @classmethod
    def validate_content(self, data):
        errors = {}
        for key, format in self.child_formats:
            error = format.validate_content(data[key])
            if error:
                errors[key] = error
        return errors or super(Object, self).validate_content(data)

    @classmethod
    def dump(self, data: model_type) -> formatted_type:
        formatted_data = self.get_extra(data)
        for key, format in self.child_formats:
            data_key = format.formatted_name
            formatted_data[data_key] = format.dump(data[key])
        return formatted_data

    @classmethod
    def compile_dump_item(self, scope, key):
        return scope + '["' + key + '"]'
