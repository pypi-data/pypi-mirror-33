import copy
from typing import Type

from pyjo import Field, ModelMetaclass, ListField
from six import iteritems

from pyjo_mdl.helpers import number_validator, cast_bool, string_validator, url_validator, embedded_validator, cast_int, \
    cast_float
from pyjo_mdl.model_classes import ValidatableModel
from .exceptions import ModelValidationError

__author__ = 'xelhark'

BASE_FIELD_PROPERTIES = {
    'integer': {
        'type': int,
        'model_validator': None,
        'validator': number_validator,
        'cast': cast_int
    },
    'float': {
        'type': float,
        'model_validator': None,
        'validator': number_validator,
        'cast': cast_float
    },
    'boolean': {
        'type': bool,
        'cast': cast_bool,
    },
    'string': {
        'type': str,
        'model_validator': None,
        'validator': string_validator,
    },
    'url': {
        'type': str,
        'model_validator': None,
        'validator': url_validator,
    },
    'embedded': {
        'type': None,
        'validator_factory': embedded_validator,
    },
    'array': {
        'type': None,
        'field': ListField,
        'field_kwargs': {
            'inner_field': lambda fs, *args, **kwargs: field_from_structure(fs['element'], *args, **kwargs),
        },
        'model_validator': None,
    },
}


def field_from_structure(fs, fields_definitions, base_class=None):
    if not isinstance(fs, dict):
        raise ModelValidationError("Invalid model. It should be a dictionary with a \'type\' property.")
    if 'type' not in fs:
        raise ModelValidationError("No \'type\' property found.")

    if fs['type'] not in fields_definitions:
        raise ModelValidationError("Unsupported field type: {}".format(fs['type']))

    props = fields_definitions[fs['type']]

    vf = props.get('validator_factory')
    if vf:
        validator = vf(field_structure=fs, fields_properties=fields_definitions, base_class=base_class)
    else:
        validator = lambda value: props.get('validator', lambda *args, **kwargs: None)(fs, value)

    field_cls = props.get('field', Field)
    field_kwargs = dict(
        type=props.get('type'),
        cast=props.get('cast'),
        validator=validator,
        required=fs.get('required', True),
    )
    if field_cls != Field and 'field_kwargs' in props:
        del field_kwargs['type']
        other_field_kwargs = {}
        for k, v in iteritems(props.get('field_kwargs')):
            if callable(v):
                v = v(fs, fields_definitions, base_class=base_class)
            other_field_kwargs[k] = v
        field_kwargs.update(other_field_kwargs)

    return field_cls(**field_kwargs)


T = Type[ValidatableModel]


def pyjo_model_from_structure(
        structure: dict,
        base_class: T = ValidatableModel,
        fields_properties: dict = None
) -> T:
    fields = {}
    errors = []

    fields_definitions = copy.deepcopy(BASE_FIELD_PROPERTIES)
    if fields_properties:
        fields_definitions.update(fields_properties)

    for element_key, field_structure in structure.items():
        if element_key in fields:
            error = ModelValidationError("Duplicate field definition: {}".format(element_key))
            errors.append(error)

        if element_key[0] == '_':
            error = ModelValidationError("First character of field cannot be '_': {}".format(element_key))
            errors.append(error)

        try:
            fields[element_key] = field_from_structure(field_structure, fields_definitions, base_class=base_class)
        except ModelValidationError as err:
            errors.append(err)

    if errors:
        raise ModelValidationError("Invalid model", errors_list=errors)
    return ModelMetaclass.__new__(ModelMetaclass, "Validator", (base_class,), fields)
