from flask import jsonify


def http_error_404():
    return jsonify({
        "error": "Not Found",
        "errorMessage": "The server has not found anything matching the request URI"
    }), 404


def http_error_405():
    return jsonify({
        "error": "Method Not Allowed",
        "errorMessage": "The method specified in the request is "
                        "not allowed for the resource identified by the request URI"
    }), 405


def unhandled_server_error_500():
    return jsonify({  # May be inconsistent with official API
        "error": "Internal Server Error",
        "errorMessage": "The server encountered an unrecoverable error while trying to fulfill your request"
    }), 500
