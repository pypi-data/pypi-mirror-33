# encoding=utf-8

from abc import ABCMeta, abstractmethod
from collections import Iterable


class ValidatorException(Exception):
    pass


"""
Here are some predefined validators.

To create a custom validator, extend the Validator class and provide the `validate`
instance method.
"""


class Validator(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def validate(self, field):
        """The function that runs the validator validation on the field"""
        pass


class WithEvery(Validator):
    def __init__(self, validator):
        self._validator = validator

    def validate(self, fields):
        for field in fields:
            if not self._validator.validate(field):
                return False
        return True


class Required(Validator):
    def validate(self, field):
        if isinstance(field, Iterable):
            return bool(field)
        return field is not None


class Equals(Validator):
    def __init__(self, value):
        self._value = value

    def validate(self, field):
        return field == self._value


class Range(Validator):
    """
    ```python
    validators.Range(10, 20)        # 10 >= number <= 20
    validators.Range(10)            # number >= 10
    validators.Range(None, 10)      # number <= 10
    ```
    """
    def __init__(self, min_value=None, max_value=None):
        self._min = min_value
        self._max = max_value

    def validate(self, field):
        is_valid = field is not None
        if self._min is not None and is_valid:
            is_valid = field >= self._min
        if self._max is not None and is_valid:
            is_valid = field <= self._max
        return is_valid


class Length(Validator):
    """
    ```python
    validators.Length(10, 20)       # 10 >= length <= 20
    validators.Length(10)           # length == 10
    validators.Length(10, None)     # length >= 10
    validators.Length(None, 10)     # length <= 10
    ```
    """
    def __init__(self, *args):
        if len(args) == 2:
            self._min = args[0]
            self._max = args[1]
        elif len(args) == 1:
            self._length = args[0]
        else:
            raise ValidatorException('Must pass either 1 or 2 arguments to the Length validator')

    def validate(self, field):
        is_valid = field is not None
        if hasattr(self, '_length') and is_valid:
            return len(field) == self._length

        if self._min is not None and is_valid:
            is_valid = len(field) >= self._min
        if self._max is not None and is_valid:
            is_valid = len(field) <= self._max
        return is_valid
