from flask import jsonify


class Error:
    error: str
    message: str
    status: int

    def __init__(self, error: str = "Generic", message: str = "Generic Server Error", status: int = 500):
        self.error = error
        self.message = message
        self.status = status

    @property
    def dual(self):
        """:rtype: (flask.Response, int)"""
        return self.jsonify, self.status

    @property
    def jsonify(self):
        """:rtype: flask.Response"""
        return jsonify(self.dict)

    @property
    def dict(self) -> dict:
        return {
            "error": self.error,
            "errorMessage": self.message,
        }


NOT_FOUND = Error("Not Found", "The server has not found anything matching the request URI", 404)
METHOD_NOT_ALLOWED = Error("Method Not Allowed", "The method specified in the request is "
                                                 "not allowed for the resource identified by the request URI", 405)
INTERNAL_ERROR = Error("Internal Server Error", "The server encountered an unrecoverable "
                                                "error while trying to fulfill your request", 500)

AUTH_HEADER_MISSING = Error("Unauthorized", "The request requires user authentication", 403)

NULL_ACCESS_TOKEN = Error("IllegalArgumentException", "Access Token can not be null or empty.", 400)
NULL_CLIENT_TOKEN = Error("IllegalArgumentException", "Missing clientToken.", 403)
INVALID_SKIN = Error("IllegalArgumentException", "Provided skin is not valid.", 400)
INVALID_UUID = Error("IllegalArgumentException", "Invalid UUID", 400)
INVALID_TOKEN = Error("ForbiddenOperationException", "Invalid token", 403)
INVALID_TIMESTAMP = Error("IllegalArgumentException", "Invalid timestamp.", 400)
INVALID_CREDENTIALS = Error("ForbiddenOperationException", "Invalid credentials. Invalid username or password.", 403)
INVALID_CREDENTIALS_RATE_LIMIT = Error("TooManyRequestsException", "Invalid credentials. "
                                                                   "Invalid username or password.", 429)
INVALID_IMAGE = Error("IllegalArgumentException", "Provided image is illegal or invalid.", 400)

OVER_PROFILE_LIMIT = Error("IllegalArgumentException", "Not more than 10 profile name per call is allowed.", 400)
PROFILE_ALREADY_ASSIGNED = Error("IllegalArgumentException", "Access token already has a profile assigned.", 400)

MISSING_SKIN = Error("IllegalArgumentException", "Model or skin URL missing.", 400)
NULL_MESSAGE = Error("IllegalArgumentException", "message is marked non-null but is null", 400)

UNTRUSTED_IP = Error("ForbiddenOperationException", "Current IP is not secured", 403)
INCORRECT_ANSWERS = Error("ForbiddenOperationException", "At least one answer was incorrect", 403)
