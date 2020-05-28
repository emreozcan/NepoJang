from functools import wraps

from flask import request

from constant.error import BAD_REQUEST


def require_json(original_function):
    @wraps(original_function)
    def inner_function(*args, **kwargs):
        if request.json is None:
            return BAD_REQUEST.dual
        return original_function(*args, **kwargs)
    return inner_function
