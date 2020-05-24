from flask import jsonify
from pony.orm import db_session

from constant.error import OVER_PROFILE_LIMIT
from db import Profile


@db_session
def json_and_response_code(request):
    if len(request.json) > 10:
        return OVER_PROFILE_LIMIT.dual

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
