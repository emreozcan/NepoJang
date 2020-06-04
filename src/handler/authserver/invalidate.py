from uuid import UUID

import jwt
from pony.orm import db_session

from db import AccessToken
from util.auth import read_yggt
from util.decorators import require_json


@db_session
@require_json
def json_and_response_code(request):
    if "accessToken" not in request.json:
        return "", 204

    try:
        yggt = UUID(read_yggt(request.json["accessToken"]))
        access_tokens = AccessToken.select(lambda tkn: tkn.uuid == yggt)
        if "clientToken" in request.json:
            request_client_token_uuid = UUID(request.json["clientToken"])
            access_tokens = access_tokens.filter(lambda tkn: tkn.client_token.uuid == request_client_token_uuid)
    except (jwt.exceptions.DecodeError, ValueError):
        return "", 204

    access_tokens.delete()

    return "", 204
