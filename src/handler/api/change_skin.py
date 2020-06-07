from io import BytesIO
from uuid import UUID

from PIL import Image, UnidentifiedImageError
from flask import Request
from pony.orm import db_session
from requests import get

from util.exceptions import InvalidAuthHeaderException
from constant.error import INVALID_SKIN, INVALID_UUID, INVALID_TOKEN, AUTH_HEADER_MISSING, MISSING_SKIN, NULL_MESSAGE, \
    INVALID_IMAGE, UNTRUSTED_IP
from db import AccessToken, Profile


def set_skin(readable, model, profile: Profile):
    try:
        image: Image = Image.open(readable)
    except (FileNotFoundError, UnidentifiedImageError, ValueError):
        # May be inconsistent with official API
        return INVALID_IMAGE.dual

    try:
        profile.update_skin(image, model)
    except ValueError:
        # May be inconsistent with official API
        return INVALID_SKIN.dual

    return "", 204


@db_session
def json_and_response_code(request: Request, uuid):
    try:
        token = AccessToken.from_header(request.headers.get("Authorization"))
    except InvalidAuthHeaderException:
        return AUTH_HEADER_MISSING.dual
    if token is None:
        # May be inconsistent with official API
        return INVALID_TOKEN.dual

    try:
        uuid_object = UUID(uuid)
    except ValueError:
        # May be inconsistent with official API
        return INVALID_UUID.dual

    profile: Profile = Profile.get(uuid=uuid_object)
    if profile is None or profile.account != token.client_token.account:
        # May be inconsistent with official API
        return INVALID_TOKEN.dual

    if not profile.account.does_trust_ip(request.remote_addr):
        return UNTRUSTED_IP.dual

    if request.method == "POST":
        if "model" not in request.form or "url" not in request.form:
            # May be inconsistent with official API
            return MISSING_SKIN.dual

        response = get(request.form["url"])
        return set_skin(BytesIO(response.content), request.form["model"], profile)

    elif request.method == "PUT":
        if "file" not in request.files or "model" not in request.form:
            # May be inconsistent with official API
            return NULL_MESSAGE.dual
        return set_skin(request.files["file"].stream, request.form["model"], profile)

    elif request.method == "DELETE":
        profile.reset_skin()
        return "", 204

    return "", 204
