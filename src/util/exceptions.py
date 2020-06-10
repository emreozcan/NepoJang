class NepoJangException(Exception):
    pass


class AuthorizationException(NepoJangException):
    pass


class InvalidAuthHeaderException(AuthorizationException):
    pass


class ExistsException(NepoJangException):
    """A field that was supposed to be unique would not be unique if this operation was completed."""
    pass
