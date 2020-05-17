from json import loads, decoder
from uuid import UUID
from flask import jsonify

import jwt

from db import AccessToken, db_session
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
        return "", 204

    try:
        yggt = UUID(read_yggt(request_data["accessToken"]))
        access_tokens = AccessToken.select(lambda tkn: tkn.uuid == yggt)
        if "clientToken" in request_keys:
            request_client_token_uuid = UUID(request_data["clientToken"])
            access_tokens = access_tokens.filter(lambda tkn: tkn.client_token.uuid == request_client_token_uuid)
    except (jwt.exceptions.DecodeError, ValueError):
        return "", 204

    access_tokens.delete()

    return "", 204
