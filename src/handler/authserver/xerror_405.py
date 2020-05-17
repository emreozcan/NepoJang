from flask import jsonify


def json_and_response_code():
    return jsonify({
        "error": "Method Not Allowed",
        "errorMessage": "The method specified in the request is not allowed for the resource identified by the request URI"
    }), 405
