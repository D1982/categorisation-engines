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

    def __init__(self, message, result_list):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.text = message
        self.result_list = result_list
