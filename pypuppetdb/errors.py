class APIError(Exception):
    """Our base exception the other errors inherit from."""
    pass


class ImproperlyConfiguredError(APIError):
    """This exception is thrown when the API is initialised
    and it detects incompatbile configuration such as SSL turned
    on but no certificates provided."""
    pass


class EmptyResponseError(APIError):
    """Will be thrown when we did recieve a response but the
    response is empty."""
    pass


class DoesNotComputeError(APIError):
    """This error will be thrown when a function is called with
    an incompatible set of optional parameters. This is the 'you are
    being a naughty developer, go read the docs' error.
    """
    pass
