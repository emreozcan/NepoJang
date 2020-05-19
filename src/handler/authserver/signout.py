from json import loads, decoder
from flask import jsonify
from pony.orm import db_session

from db import AccessToken
from handler.authserver._username_password_verify import account_or_none


@db_session
def json_and_response_code(request):
    if "username" not in request.json or "password" not in request.json:
        return jsonify({
            "error": "TooManyRequestsException",
            "errorMessage": "Invalid credentials. Invalid username or password."
        }), 429

    account = account_or_none(request.json["username"], request.json["password"])
    if account is None:
        return jsonify({
            "error": "ForbiddenOperationException",
            "errorMessage": "Invalid credentials. Invalid username or password."
        }), 403

    AccessToken.select(lambda tkn: tkn.client_token.account == account).delete()

    return "", 204
