from pyjo import Model
from pyjo.exceptions import FieldTypeError, RequiredFieldError
from six import iteritems

from pyjo_mdl.exceptions import InstanceValidationError

__author__ = 'xelhark'


class ValidatableModel(Model):

    @classmethod
    def validate(cls, values):
        for key, field in iteritems(cls._fields):
            field.cast_and_validate(values.get(key, None))


class FullErrorValidation(ValidatableModel):
    def __init__(self, **kwargs):
        errors = []
        for key, value in iteritems(kwargs):
            try:
                self._fields[key].cast_and_validate(value)
            except InstanceValidationError as err:
                if err.errors_list:
                    errors.extend(err.errors_list)
                else:
                    err = InstanceValidationError("Error validating field \'{}\': {}".format(key, str(err)))
                    errors.append(err)

        if errors:
            raise InstanceValidationError("Error validating instance.", errors_list=errors)
        super(FullErrorValidation, self).__init__(**kwargs)

    @classmethod
    def validate(cls, values):
        errors = []
        for key, field in iteritems(cls._fields):
            try:
                field.cast_and_validate(values.get(key))
            except (InstanceValidationError, FieldTypeError, RequiredFieldError) as err:
                err = InstanceValidationError("Error validating field \'{}\': {}".format(key, str(err)))
                errors.append(err)
        if errors:
            raise InstanceValidationError("Error validating instance.", errors_list=errors)
