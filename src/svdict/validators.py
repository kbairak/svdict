from collections.abc import Mapping, Sequence

from jsonschema import Draft7Validator
from jsonschema.validators import extend as extend_validator


def _is_mapping(checker, instance):
    return (Draft7Validator.TYPE_CHECKER.is_type(instance, "object") or
            isinstance(instance, Mapping))


def _is_sequence(checker, instance):
    return (Draft7Validator.TYPE_CHECKER.is_type(instance, "array") or
            isinstance(instance, Sequence))


_type_checker = Draft7Validator.TYPE_CHECKER
_type_checker = _type_checker.redefine("object", _is_mapping)
_type_checker = _type_checker.redefine("array", _is_sequence)
SVValidator = extend_validator(Draft7Validator, type_checker=_type_checker)
