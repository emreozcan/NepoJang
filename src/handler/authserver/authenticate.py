from uuid import UUID

from flask import jsonify

import jwt
from pony.orm import db_session

from constant.error import INVALID_CREDENTIALS, INVALID_TOKEN, NULL_MESSAGE
from db import ClientToken, Profile, AccessToken
from util.auth import attempt_login
from util.crypto.jwtkeys import JWT_PRIVATE_KEY_BYTES
from util.decorators import require_json


@db_session
@require_json
def json_and_response_code(request):
    if "username" not in request.json or "password" not in request.json:
        return NULL_MESSAGE.dual

    account = attempt_login(request.json["username"], request.json["password"])
    if account is None:
        return INVALID_CREDENTIALS.dual

    client_token: ClientToken
    if "clientToken" not in request.json:
        client_token = ClientToken(account=account)
        client_token_string = client_token.uuid.hex
    else:
        try:
            client_token_uuid = UUID(request.json["clientToken"])
        except ValueError:
            return INVALID_TOKEN.dual

        client_token = ClientToken.get(uuid=client_token_uuid)
        if client_token is not None and client_token.account != account:
            client_token.account = account

        elif client_token is None:  # there's no client token with requested UUID
            client_token = ClientToken(account=account, uuid=client_token_uuid)

        else:  # requested clientToken exists and owned by authorized account
            client_token.refresh()

        client_token_string = request.json["clientToken"]

    optional_profile = {}
    if "agent" in request.json:
        available_profiles = list(
            Profile.select(lambda p: p.agent == request.json["agent"]["name"] and p.account == account))
        if len(available_profiles) == 1:
            optional_profile = {"profile": available_profiles[0]}

    access_token = AccessToken(
        client_token=client_token,
        **optional_profile
    )

    response_data = {
        "accessToken": jwt.encode(access_token.format(), key=JWT_PRIVATE_KEY_BYTES, algorithm="RS256").decode(),
        "clientToken": client_token_string
    }

    if "requestUser" in request.json and request.json["requestUser"]:
        response_data["user"] = {
            "username": account.username,
            "id": account.uuid.hex
        }

    response_data["availableProfiles"] = []
    if "agent" in request.json:
        for profile in available_profiles:
            response_data["availableProfiles"].append({
                "name": profile.name,
                "id": profile.uuid.hex,
            })

        if len(available_profiles) == 1:
            response_data["selectedProfile"] = response_data["availableProfiles"][0]

    for token in AccessToken \
            .select(lambda candidate: candidate.client_token.account == account and candidate != access_token):
        token.authentication_valid = False

    return jsonify(response_data), 200
