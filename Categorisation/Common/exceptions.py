"""Custom Exceptions."""


class ResponseMissingEntries(Exception):

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
