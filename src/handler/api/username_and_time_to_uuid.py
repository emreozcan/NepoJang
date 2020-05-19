from datetime import datetime

from flask import jsonify
from pony.orm import db_session

from db import Profile


@db_session
def json_and_response_code(request, username):
    if "at" not in request.args:
        at = datetime.utcnow()
    else:
        try:
            at = datetime.fromtimestamp(int(request.args["at"]))
        except (ValueError, OSError):
            return jsonify({
                "error": "IllegalArgumentException",
                "errorMessage": "Invalid timestamp."
            }), 400

    event = Profile.get_owner_profile_at(username, at)
    if event is None:
        return "", 204

    return jsonify({
        "id": event.profile.uuid.hex,
        "name": event.profile.name
    }), 200
