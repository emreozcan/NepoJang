from flask import jsonify


def json_and_response_code():
    return jsonify({
        "error": "Not Found",
        "errorMessage": "The server has not found anything matching the request URI"
    }), 404
