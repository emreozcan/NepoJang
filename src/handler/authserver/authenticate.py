from datetime import timedelta
from json import loads, decoder

import jwt
from flask import jsonify

from db import *
from password import password_compare


@db_session
def authenticate(request):
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

    accounts = list(Account.select(lambda a: a.username == request_data["username"]))
    if len(accounts) != 1 or not password_compare(request_data["password"], accounts[0].password):
        return jsonify({
            "error": "ForbiddenOperationException",
            "errorMessage": "Invalid credentials. Invalid username or password."
        }), 403

    if "clientToken" not in request_keys:
        client_token = ClientToken(account=accounts[0])
    else:
        try:
            client_token = ClientToken(account=accounts[0], uuid=UUID(request_data["clientToken"]))
        except ValueError as e:
            return jsonify({
                "error": type(e),
                "errorMessage": e.args[0]
            }), 400

    optional_profile = {}
    if "agent" in request_keys:
        available_profiles = list(
            Profile.select(lambda p: p.agent == request_data["agent"]["name"] and p.account == accounts[0]))
        if len(available_profiles) == 1:
            optional_profile = {"profile": available_profiles[0]}

    utcnow = datetime.utcnow()
    access_token = AccessToken(
        issuer="Yggdrasil-Auth",
        created_utc=utcnow,
        expiry_utc=utcnow + timedelta(days=2),
        authentication_valid=True,
        account=accounts[0],
        client_token=client_token,
        **optional_profile
    )

    response_data = {
        "accessToken": jwt.encode({
            "sub": accounts[0].uuid.hex,
            "yggt": access_token.uuid.hex,
            "issr": access_token.issuer,
            "exp": int(access_token.expiry_utc.timestamp()),
            "iat": int(access_token.created_utc.timestamp())
        }, key="").decode(),
        "clientToken": client_token.uuid.hex
    }

    if "requestUser" in request_keys and request_data["requestUser"]:
        response_data["user"] = {
            "username": accounts[0].username,
            "id": accounts[0].uuid.hex
        }

    if "profile" in optional_profile:
        response_data["selectedProfile"] = {
            "name": optional_profile["profile"].name,
            "id": optional_profile["profile"].uuid.hex
        }
        response_data["availableProfiles"] = [response_data["selectedProfile"]]

    for token in AccessToken \
            .select(lambda candidate: candidate.account == accounts[0] and candidate != access_token):
        token.authentication_valid = False

    return response_data, 200
