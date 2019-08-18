"""Custom Exceptions."""

import Categorisation.Tink.model as model


# Castlight related exception classes
class ResponseMissingEntriesError(Exception):

    """
    Exception that can be raised whenever there are missing data response to an api request.
    """

    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.text = message


class TestModeWarning(Exception):

    """
    Exception that can be raised in order to indicate that an application is running in test mode.
    """

    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.text = message


# Tink related exception classes
class UserNotExistingError(Exception):

    """
    Exception that indicates that a user does not exist within the Tink platform.
    """

    def __init__(self, message, result_list):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.text = message
        self.result_list = result_list


class ParameterError(Exception):

    """
    Exception that indicates that parameter had not the expected value(s)
    """

    def __init__(self, param_name: str, expected_type: str, found_type: str,
                 result_list=None):
        """
        Initialization of a ParmeterError.
        :param param_name: Name of the parameter.
        :param expected_type: Expected datatype of the parameter.
        :param found_type: Actual data type of the parameter.
        :param result_list: An optional reference to a model.TinkModelResult
        object in order to transfer results of the stopped operation back to
        the caller.
        """
        # Call the base class constructor with the parameters it needs
        self.text = f'Parameter: {param_name} has an unexpected type {found_type}. ' \
                    f'Possible type(s): {expected_type}'

        super().__init__(self.text)

        if result_list and isinstance(result_list, model.TinkModelResultList):
            self.result_list = result_list
        else:
            self.result_list = model.TinkModelResultList()
