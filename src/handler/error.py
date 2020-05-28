from constant.error import NOT_FOUND, METHOD_NOT_ALLOWED, INTERNAL_ERROR, JSON_INVALID


def http_error_400():
    return JSON_INVALID.dual


def http_error_404():
    return NOT_FOUND.dual


def http_error_405():
    return METHOD_NOT_ALLOWED.dual


def unhandled_server_error_500():
    # May be inconsistent with official API
    return INTERNAL_ERROR.dual
