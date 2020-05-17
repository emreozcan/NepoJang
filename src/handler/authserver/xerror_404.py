from flask import jsonify


def xerror_404():
    return jsonify({
        "error": "Not Found",
        "errorMessage": "The server has not found anything matching the request URI"
    }), 404
