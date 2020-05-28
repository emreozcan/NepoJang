from uuid import UUID

from pony.orm import db_session

from constant.error import NULL_ACCESS_TOKEN, INVALID_TOKEN
from db import AccessToken, ClientToken
from util.decorators import require_json


@db_session
@require_json
def json_and_response_code(request):
    if "accessToken" not in request.json:
        return NULL_ACCESS_TOKEN.dual

    access_token = AccessToken.from_token(request.json["accessToken"])
    if access_token is None:
        return INVALID_TOKEN.dual

    if "clientToken" in request.json:
        try:
            request_client_token_uuid = UUID(request.json["clientToken"])
            client_token = ClientToken.get(lambda t: t.uuid == request_client_token_uuid)
        except ValueError:
            client_token = None

        if client_token is None or client_token != access_token.client_token:
            return INVALID_TOKEN.dual

    if not access_token.authentication_valid:
        return INVALID_TOKEN.dual

    return "", 204
