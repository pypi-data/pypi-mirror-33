from .object import Object


class Dict(Object):
    model_type = dict
    formatted_type = dict
    schema_class = object

    @staticmethod
    def get_model_value(data, key):
        return data[key]
