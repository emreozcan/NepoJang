class NepoJangException(Exception):
    pass


class AuthorizationException(NepoJangException):
    pass


class InvalidAuthHeaderException(AuthorizationException):
    pass


class InvalidTokenException(AuthorizationException):
    pass

