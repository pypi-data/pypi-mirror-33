from .raw_format import RawFormat


class NoneType(RawFormat):
    model_type = None.__class__
    formatted_type = None.__class__
