from io import BytesIO
from uuid import UUID

from PIL import Image, UnidentifiedImageError
from flask import Request
from pony.orm import db_session
from requests import get

from constant.error import INVALID_SKIN, INVALID_UUID, INVALID_TOKEN, AUTH_HEADER_MISSING, MISSING_SKIN, NULL_MESSAGE, \
    INVALID_IMAGE
from db import AccessToken, Profile


def set_skin(readable, model, profile: Profile):
    try:
        image: Image = Image.open(readable)
    except (FileNotFoundError, UnidentifiedImageError, ValueError):
        # May be inconsistent with official API
        return INVALID_IMAGE.dual

    try:
        profile.skin_update(image, model)
    except ValueError:
        # May be inconsistent with official API
        return INVALID_SKIN.dual

    return "", 204


@db_session
def json_and_response_code(request: Request, uuid):
    auth = request.headers.get("Authorization")
    if auth is None or not auth.startswith("Bearer ") or auth == "Bearer ":
        return AUTH_HEADER_MISSING.dual

    auth = auth[7:]
    token = AccessToken.from_token(auth)
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
        profile.skin_delete()
        return "", 204

    return "", 204
