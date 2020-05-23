from uuid import UUID
from io import BytesIO

from pony.orm import db_session
from requests import get
from PIL import Image

from flask import Request, jsonify

from db import AccessToken, Profile


def set_skin(readable, model, profile: Profile):
    try:
        image: Image = Image.open(readable)
    except Exception as e:
        return jsonify({  # May be inconsistent with official API
            "error": str(type(e)),
            "errorMessage": e.args[0]
        }), 400

    try:
        profile.skin_update(image, model)
    except ValueError:
        return jsonify({  # May be inconsistent with official API
            "error": "IllegalArgumentException",
            "errorMessage": "Provided skin is not valid."
        }), 400

    return "", 204


@db_session
def json_and_response_code(request: Request, uuid):
    auth = request.headers.get("Authorization")
    if auth is None or not auth.startswith("Bearer ") or auth == "Bearer ":
        return jsonify({
            "error": "Unauthorized",
            "errorMessage": "The request requires user authentication",
        }), 403

    auth = auth[7:]
    token = AccessToken.from_token(auth)
    if token is None:
        return jsonify({  # May be inconsistent with official API
            "error": "ForbiddenOperationException",
            "errorMessage": "Invalid token",
        }), 403

    try:
        uuid_object = UUID(uuid)
    except ValueError:
        return jsonify({  # May be inconsistent with official API
            "error": "IllegalArgumentException",
            "errorMessage": "Invalid UUID",
        }), 400
    
    profile: Profile = Profile.get(uuid=uuid_object)
    if profile is None or profile.account != token.client_token.account:
        return jsonify({  # May be inconsistent with official API
            "error": "ForbiddenOperationException",
            "errorMessage": "Invalid token"
        }), 403

    if request.method == "POST":
        if "model" not in request.form or "url" not in request.form:
            return jsonify({  # May be inconsistent with official API
                "error": "IllegalArgumentException",
                "errorMessage": "Model or skin URL missing."
            }), 400
        response = get(request.form["url"])
        return set_skin(BytesIO(response.content), request.form["model"], profile)

    elif request.method == "PUT":
        if "file" not in request.files or "model" not in request.form:
            return jsonify({  # May be inconsistent with official API
                "error": "IllegalArgumentException",
                "errorMessage": "message is marked non-null but is null"
            }), 400
        return set_skin(request.files["file"].stream, request.form["model"], profile)

    elif request.method == "DELETE":
        profile.skin_delete()
        return "", 204

    return "", 204
