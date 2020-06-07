from uuid import UUID

from flask import jsonify
from pony.orm import db_session

from db import Profile
from util.public_profile_details import get_public_profile_details


@db_session
def json_and_response_code(request, uuid, textures_host):
    try:
        uuid_object = UUID(uuid)
    except ValueError:
        return "", 204

    profile = Profile.get(uuid=uuid_object)
    if profile is None:
        return "", 204

    unsigned = request.args.get("unsigned")
    if unsigned is not None and unsigned == "false":
        return jsonify(get_public_profile_details(profile, False, textures_host)), 200
    return jsonify(get_public_profile_details(profile, True, textures_host)), 200
