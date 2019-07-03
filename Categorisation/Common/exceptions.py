"""Custom Exceptions."""

"""Exception that can be raised whenever there are missing data response to an api request."""
class ResponseMissingEntries(Exception):

    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.text = message


"""Exception that can be raised in order to indicate that an application is running in test mode."""
class TestModeWarning(Exception):

    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.text = message
