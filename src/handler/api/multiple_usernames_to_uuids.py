from flask import jsonify
from pony.orm import db_session

from db import Profile


@db_session
def json_and_response_code(request):
    if len(request.json) > 10:
        return jsonify({
            "error": "IllegalArgumentException",
            "errorMessage": "Not more than 10 profile name per call is allowed."
        }), 400

    uuids = []

    for name in request.json:
        profile = Profile.get_profile_with_name(name)
        if profile is None:
            continue

        uuids.append({
            "id": profile.uuid.hex,
            "name": profile.name
        })

    return jsonify(uuids), 200
