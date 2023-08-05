from typing import List, Any
from .format_registry import FormatRegistry
from . import formats


integer_string = FormatRegistry.build_type(formats.IntegerString)


def setup():
    FormatRegistry.set_default(formats.NoneType)
    FormatRegistry.set_default(formats.Any)
    FormatRegistry.set_default(formats.String)
    FormatRegistry.set_default(formats.Float)
    FormatRegistry.set_default(formats.Integer)
    FormatRegistry.set_default(formats.DecimalString)
    FormatRegistry.set_default(formats.DateString)
    FormatRegistry.set_generic_default(formats.Union)
    FormatRegistry.set_generic_default(formats.List)
    FormatRegistry.set_default(formats.List.from_type(List[Any]), list)
