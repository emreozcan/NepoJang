from datetime import timedelta
from json import loads, decoder

import jwt
from flask import jsonify

from db import *
from handler.authserver._username_password_verify import account_or_none
from password import password_compare


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

    if "username" not in request_keys or "password" not in request_keys:
        return jsonify({
            "error": "IllegalArgumentException",
            "errorMessage": "message is marked non-null but is null"
        }), 400

    account = account_or_none(request_data["username"], request_data["password"])
    if account is None:
        return jsonify({
            "error": "ForbiddenOperationException",
            "errorMessage": "Invalid credentials. Invalid username or password."
        }), 403

    if "clientToken" not in request_keys:
        client_token = ClientToken(account=account)
    else:
        try:
            client_token = ClientToken(account=account, uuid=UUID(request_data["clientToken"]))
        except ValueError as e:
            return jsonify({
                "error": type(e),
                "errorMessage": e.args[0]
            }), 400

    optional_profile = {}
    if "agent" in request_keys:
        available_profiles = list(
            Profile.select(lambda p: p.agent == request_data["agent"]["name"] and p.account == account))
        if len(available_profiles) == 1:
            optional_profile = {"profile": available_profiles[0]}

    utcnow = datetime.utcnow()
    access_token = AccessToken(
        issuer="Yggdrasil-Auth",
        created_utc=utcnow,
        expiry_utc=utcnow + timedelta(days=2),
        authentication_valid=True,
        account=account,
        client_token=client_token,
        **optional_profile
    )

    access_token_data = {
        "sub": account.uuid.hex,
        "yggt": access_token.uuid.hex,
        "issr": access_token.issuer,
        "exp": int(access_token.expiry_utc.timestamp()),
        "iat": int(access_token.created_utc.timestamp())
    }

    if "profile" in optional_profile:
        access_token_data["spr"] = optional_profile["profile"].uuid.hex

    response_data = {
        "accessToken": jwt.encode(access_token_data, key="").decode(),
        "clientToken": client_token.uuid.hex
    }

    if "requestUser" in request_keys and request_data["requestUser"]:
        response_data["user"] = {
            "username": account.username,
            "id": account.uuid.hex
        }

    if "profile" in optional_profile:
        response_data["selectedProfile"] = {
            "name": optional_profile["profile"].name,
            "id": optional_profile["profile"].uuid.hex
        }
        response_data["availableProfiles"] = [response_data["selectedProfile"]]
    else:
        response_data["availableProfiles"] = []

    for token in AccessToken \
            .select(lambda candidate: candidate.account == account and candidate != access_token):
        token.authentication_valid = False

    return jsonify(response_data), 200
