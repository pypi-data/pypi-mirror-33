import re

from pyjo_mdl.exceptions import InstanceValidationError

__author__ = 'xelhark'
URL_REGEX = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')


def number_validator(fs, value):
    if 'max_value' in fs and value > fs['max_value']:
        raise InstanceValidationError(
            "Value is bigger than max value: {} > {}".format(value, fs['max_value']))
    if 'min_value' in fs and value < fs['min_value']:
        raise InstanceValidationError(
            "Value is smaller than min value: {} < {}".format(value, fs['min_value']))


def string_validator(fs, value):
    if 'max_length' in fs and len(value) > fs['max_length']:
        raise InstanceValidationError("Value {} is longer than max allowed length ({})".format(value, fs['max_length']))
    if 'validation' in fs and not re.match(fs['validation'], value):
        raise InstanceValidationError("Value {} does not match provided validation regex".format(value))
    if 'values' in fs and value not in fs['values']:
        raise InstanceValidationError(
            "Value {} does not match any value in the enum list [{}]".format(value, ', '.join(fs['values']))
        )


def url_validator(fs, value):
    if not URL_REGEX.match(value):
        raise InstanceValidationError("{} is not a valid URL.".format(value))


def embedded_validator(field_structure, *args, **kwargs):
    from pyjo_mdl.core import pyjo_model_from_structure
    return pyjo_model_from_structure(structure=field_structure['model'], *args, **kwargs).validate


def cast_bool(value):
    if isinstance(value, str):
        if value.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif value.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
    elif isinstance(value, bool):
        return value
    elif isinstance(value, int):
        return value > 0
    
    raise ValueError('Boolean value expected. Got "{}" instead'.format(value))


def cast_int(value):
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            raise ValueError('Integer value expected. Got "{}" instead'.format(value))
    return value


def cast_float(value):
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            raise ValueError('Float value expected. Got "{}" instead'.format(value))
    return value
