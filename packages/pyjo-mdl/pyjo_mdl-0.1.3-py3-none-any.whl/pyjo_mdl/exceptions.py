__author__ = 'xelhark'


class ErrorWithList(ValueError):
    def __init__(self, message, errors_list=None):
        self.errors_list = errors_list
        super(ErrorWithList, self).__init__(message)


class ModelValidationError(ErrorWithList):
    pass


class InstanceValidationError(ErrorWithList):
    pass
