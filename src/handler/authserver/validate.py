from json import loads, decoder
from uuid import UUID
from flask import jsonify

import jwt

from db import AccessToken, ClientToken, db_session
from handler.authserver._jwt_access_token import read_yggt


@db_session
def json_and_response_code(request):
    try:
        request_data = loads(request.data)
    except decoder.JSONDecodeError as e:
        return jsonify({
            "error": "JsonEOFException",
            "errorMessage": f"{e.msg}: line {e.lineno} column {e.colno} (char {e.pos})"
        }), 400
    request_keys = request_data.keys()

    if "accessToken" not in request_keys:
        return jsonify({
            "error": "IllegalArgumentException",
            "errorMessage": "Access Token can not be null or empty."
        }), 400

    try:
        yggt = UUID(read_yggt(request_data["accessToken"]))
        access_tokens = list(AccessToken.select(lambda tkn: tkn.uuid == yggt))
    except (jwt.exceptions.DecodeError, ValueError):
        return jsonify({
            "error": "ForbiddenOperationException",
            "errorMessage": "Invalid token"
        }), 403

    if len(access_tokens) != 1:
        return jsonify({
            "error": "ForbiddenOperationException",
            "errorMessage": "Invalid token"
        }), 403

    if "clientToken" in request_keys:
        try:
            request_client_token_uuid = UUID(request_data["clientToken"])
            client_tokens = list(ClientToken.select(lambda tkn: tkn.uuid == request_client_token_uuid))
        except ValueError:
            client_tokens = []
        if len(client_tokens) != 1:
            return jsonify({
                "error": "ForbiddenOperationException",
                "errorMessage": "Invalid token"
            }), 403

    if not access_tokens[0].authentication_valid:
        return jsonify({
            "error": "ForbiddenOperationException",
            "errorMessage": "Invalid token"
        }), 403

    return "", 204
