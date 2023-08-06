# encoding=utf-8
from six import iteritems


class SchemaException(Exception):
    pass


class ValidationSchema(object):
    """
    Define a class based schema that inherits from the ValidationSchema.
    All class attributes should be of type tuple with as many validators
    as wanted, before ending with the error message.

    ```python
    from object_validation import validators, ValidationSchema

    class InstanceValidationSchema(ValidationSchema):
        name = validators.IsRequired(), 'The error message'
        description = validators.IsEqual('Must equal me'), 'Messages can be formattible "{}"'
    ```

    Nested attributes should be defined with `__`, e.g. let's say we want all gigs of a campaign
    to have exactly 100 likes:
    ```python
    class HumanValidationSchema(ValidationSchema):
        eyes__eyeballs__color = IsEqual('black'), 'All eyeballs need to be `black`. Got "{}" eyeball'
    ```
    """
    @classmethod
    def get_fields(cls):
        attrs = []
        for attr_name, field_obj in iteritems(cls.__dict__):
            if attr_name.startswith('__'):
                continue
            if not isinstance(field_obj, tuple):
                raise SchemaException(
                    'Schema attributes must be of type "tuple". "{}" is of type "{}"'.format(
                        attr_name,
                        type(field_obj),
                    )
                )
            attrs.append(attr_name)
        return attrs


class Validate(object):
    """
    ```python
    from object_validation import Validate

    errors = Validate(instance, InstanceValidationSchema)
    if errors:
        raise CustomException(errors)
    ```
    """
    @staticmethod
    def _get_attr(obj, lis):
        """
        This function can get attributes of nested fields, even
        for many to many relations.

        ```python
        Validate._get_attr(obj, ['humans', 'hands', 'fingers'])
        ```
        """
        if obj is not None and len(lis):
            if isinstance(obj, list):
                attrs = []
                for o in obj:
                    attr = Validate._get_attr(getattr(o, lis[0]), lis[1:])
                    attrs.extend(attr if isinstance(attr, list) else [attr])
                return attrs
            return Validate._get_attr(getattr(obj, lis.pop(0)), lis)
        return obj

    def validate(cls, obj, schema):
        errors = []
        for attr_name in schema.get_fields():
            field_obj = cls._get_attr(obj, attr_name.split('__'))
            for validator in getattr(schema, attr_name)[:-1]:
                if not validator.validate(field_obj):
                    errors.append(getattr(schema, attr_name)[-1].format(field_obj))
                    break
        return errors

    __new__ = validate


from . import validators  # noqa
