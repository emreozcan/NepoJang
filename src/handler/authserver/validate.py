from json import loads, decoder
from uuid import UUID
from flask import jsonify

import jwt
from pony.orm import db_session

from db import AccessToken, ClientToken
from handler.authserver._jwt_access_token import read_yggt


@db_session
def json_and_response_code(request):
    if "accessToken" not in request.json:
        return jsonify({
            "error": "IllegalArgumentException",
            "errorMessage": "Access Token can not be null or empty."
        }), 400

    try:
        yggt = UUID(read_yggt(request.json["accessToken"]))
        access_token = AccessToken.get(lambda t: t.uuid == yggt)
    except (jwt.exceptions.DecodeError, ValueError):
        return jsonify({
            "error": "ForbiddenOperationException",
            "errorMessage": "Invalid token"
        }), 403

    if access_token is None:
        return jsonify({
            "error": "ForbiddenOperationException",
            "errorMessage": "Invalid token"
        }), 403

    if "clientToken" in request.json:
        try:
            request_client_token_uuid = UUID(request.json["clientToken"])
            client_token = ClientToken.get(lambda t: t.uuid == request_client_token_uuid)
        except ValueError:
            client_token = None

        if client_token is None:
            return jsonify({
                "error": "ForbiddenOperationException",
                "errorMessage": "Invalid token"
            }), 403

    if not access_token.authentication_valid:
        return jsonify({
            "error": "ForbiddenOperationException",
            "errorMessage": "Invalid token"
        }), 403

    return "", 204
