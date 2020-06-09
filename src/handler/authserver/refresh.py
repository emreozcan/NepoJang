from uuid import UUID

from flask import jsonify

import jwt
from pony.orm import db_session

from constant.error import INVALID_TOKEN, NULL_CLIENT_TOKEN, NULL_ACCESS_TOKEN, INVALID_UUID, PROFILE_NOT_FOUND
from db import AccessToken, Profile
from util.crypto.jwtkeys import JWT_PRIVATE_KEY_BYTES
from util.decorators import require_json


@db_session
@require_json
def json_and_response_code(request):
    if "clientToken" not in request.json or request.json["clientToken"] is None:
        return NULL_CLIENT_TOKEN.dual

    if "accessToken" not in request.json or request.json["accessToken"] is None:
        return NULL_ACCESS_TOKEN.dual

    access_token = AccessToken.from_token(request.json["accessToken"])
    try:
        if access_token is None or access_token.client_token.uuid != UUID(request.json["clientToken"]):
            return INVALID_TOKEN.dual
    except ValueError:
        return INVALID_UUID.dual

    if "selectedProfile" in request.json:
        try:
            _selected_uuid = UUID(request.json["selectedProfile"]["id"])
        except ValueError:
            return INVALID_UUID.dual
        new_profile = Profile.get(lambda x: x.uuid == _selected_uuid and x.name == request.json["selectedProfile"]["name"] and x.account == access_token.client_token.account)
        if new_profile is None:
            return PROFILE_NOT_FOUND.dual
    else:
        new_profile = access_token.profile

    new_access_token = AccessToken(
        client_token=access_token.client_token,
        profile=new_profile,
    )

    access_token.delete()

    response_data = {
        "accessToken": jwt.encode(new_access_token.format(), key=JWT_PRIVATE_KEY_BYTES, algorithm="RS256").decode(),
        "clientToken": request.json["clientToken"],
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
