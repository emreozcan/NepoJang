from pony.orm import db_session

from constant.error import INVALID_CREDENTIALS, INVALID_CREDENTIALS_RATE_LIMIT
from db import AccessToken
from util.auth import attempt_login
from util.decorators import require_json


@db_session
@require_json
def json_and_response_code(request):
    if "username" not in request.json or "password" not in request.json:
        return INVALID_CREDENTIALS_RATE_LIMIT.dual

    account = attempt_login(request.json["username"], request.json["password"])
    if account is None:
        return INVALID_CREDENTIALS.dual

    AccessToken.select(lambda tkn: tkn.client_token.account == account).delete()

    return "", 204
