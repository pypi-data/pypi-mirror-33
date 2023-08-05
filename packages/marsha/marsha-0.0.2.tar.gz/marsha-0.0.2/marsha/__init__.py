"""
A collection of utilities for declaring schemas using type annotations.
"""
from .format_registry import FormatRegistry
from .types import setup
from .object import Object
from .formats import Object as ObjectFormat, Dict as DictFormat


setup()


def schema(model=None, **constraints):
    """
    Build a schema. Type annotations on the schema are used to declare the
    schema's item types. Attributes values on the schema are used as default
    values. The new format is used when the model is loaded, dumped, or nested
    in another schema.

    Arguments:
        model (type, optional): The model that the schema will load to and dump
            from. Use this to specify the model if the schema and the model are
            separate classes. Defaults to using the schema as the model.
        ignore_extra (bool, optional): Discard extra values without erroring?
            Defaults to `False`.
        keep_extra (bool, optional): Keep all values even if they are not
            declared by the schema annotations? Overrides ``ignore_extra``.
            Defaults to `False`. *Note: Enabling this on object models
            requires the model's constructor to accept the extra data as
            kwargs.*

    Returns:
        decorator: A class decorator for registering a schema.

    Raises:
        AttributeError: If a constraint is provided that does not correspond to
            a method on the format.
    """
    def wrapper(schema):
        model_type = model or schema
        if issubclass(model_type, dict):
            format_type = DictFormat
        else:
            format_type = ObjectFormat

        class SchemaFormat(format_type):
            schema_class = schema
        SchemaFormat.model_type = model_type
        SchemaFormat.add_constraints(constraints, name=format_type.__name__)
        SchemaFormat.init()
        FormatRegistry.register_format(SchemaFormat)
        return schema
    return wrapper


def type(type=None, format=None, **constraints):
    """
    Build a type. The provided constraints are added to the format. The format
    is used when the new type is loaded or dumped.

    Arguments:
        type (type, optional): The type to add constraints to. If omitted, a
            format must be provided.
        format (type, optional): The format to add constrains to. If provided,
            it ignores the type argument. Defaults to the default format for
            the type. If omitted, a type must be provided.
        **constraints (Any): Constraints to add to the format. The kwarg names
            must be names of functions that are defined on the format class.
            The value of the kwarg is passed to the constraint function as its
            only argument.

    Returns:
        type: A new type suitable for use as a type annotation and in a schema.

    Raises:
        TypeError: If a type is provided that does not have a default format.
        AttributeError: If a constraint is provided that does not correspond to
            a method on the format.
    """
    format = format or FormatRegistry.get(type)

    class ConstrainedFormat(format):
        pass
    ConstrainedFormat.init()
    ConstrainedFormat.add_constraints(constraints, name=format.__name__)
    return FormatRegistry.build_type(ConstrainedFormat)


def load(data, type):
    """
    Deserialize data.

    Arguments:
        data (Any): The data to deserialize.
        type (type): The type to load the data into.

    Returns:
        Any: An instance of the type containing the deserialized data.

    Raises:
        TypeError: If the type does not have a format.
        TypeError: If any values are missing or have the wrong type.
        ValueError: If any values fail content constraints.
    """
    format = FormatRegistry.get(type)
    data, errors = format.load(data)
    if errors:
        raise TypeError(errors)
    errors = format.validate_content(data)
    if errors:
        raise ValueError(errors)
    return data


def dump(object, view=None):
    """
    Serialize data.

    Arguments:
        object (Any): An object to serialize.
        view (type, optional): The view to dump the object from. This allows
            defining an alternate format that serializes a data differently
            than the type that was used to construct the object. Defaults to
            the object's type.

    Returns:
        Any: The serialized data.

    Raises:
        TypeError: If the view does not have a format.
    """
    view = view or object.__class__
    format = FormatRegistry.get(view)
    return format.dump(object)


def validate(type):
    """
    Add custom validation. The provided function is used to validate the
    content when the type is loaded.

    Arguments:
        type (type): The type to validate.

    Returns:
        decorator: A function decorator for registering a validator.

    Raises:
        TypeError: If the type does not have a format.
    """
    format = FormatRegistry.get(type)

    def wrapper(validator):
        format.add_validator(validator)
        return validator
    return wrapper


__all__ = ['Object', 'type', 'schema', 'validate', 'dump', 'load']
