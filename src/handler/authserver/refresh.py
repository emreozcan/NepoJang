from json import loads, decoder
from uuid import UUID
from flask import jsonify

import jwt
from pony.orm import db_session

from handler.authserver._jwt_access_token import read_yggt
from db import AccessToken


@db_session
def json_and_response_code(request):
    if "clientToken" not in request.json or request.json["clientToken"] is None:
        return jsonify({
            "error": "IllegalArgumentException",
            "errorMessage": "Missing clientToken."
        }), 403

    if "accessToken" not in request.json or request.json["accessToken"] is None:
        return jsonify({
            "error": "IllegalArgumentException",
            "errorMessage": "Access Token can not be null or empty."
        }), 400

    if "selectedProfile" in request.json:
        return jsonify({
            "error": "IllegalArgumentException",
            "errorMessage": "Access token already has a profile assigned."
        }), 400

    try:
        yggt = UUID(read_yggt(request.json["accessToken"]))
        request_client_token_uuid = UUID(request.json["clientToken"])
        access_token = AccessToken.get(lambda t: t.client_token.uuid == request_client_token_uuid and t.uuid == yggt)
    except (jwt.exceptions.DecodeError, ValueError):
        return jsonify({
            "error": "ForbiddenOperationException",
            "errorMessage": "Invalid token"
        }), 403

    if access_token is None:
        return jsonify({
            "error": "ForbiddenOperationException",
            "errorMessage": "Invalid token."
        }), 403

    new_access_token = AccessToken(
        client_token=access_token.client_token,
        profile=access_token.profile
    )

    access_token.delete()

    response_data = {
        "accessToken": jwt.encode(new_access_token.format(), key="").decode(),
        "clientToken": new_access_token.client_token.uuid.hex,
    }

    if new_access_token.profile:
        response_data["selectedProfile"] = {
            "id": new_access_token.profile.uuid.hex,
            "name": new_access_token.profile.name
        }

    if "requestUser" in request.json and request.json["requestUser"]:
        response_data["user"] = {
            "id": new_access_token.client_token.account.uuid.hex,
            "username": new_access_token.client_token.account.username
        }

    return jsonify(response_data), 200
