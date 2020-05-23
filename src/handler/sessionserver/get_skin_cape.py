from base64 import b64encode
from json import dumps
from uuid import UUID

from flask import jsonify
from pony.orm import db_session

from db import Profile


@db_session
def json_and_response_code(request, uuid, textures_host):
    try:
        uuid_object = UUID(uuid)
    except ValueError:
        return "", 204

    profile = Profile.get(uuid=uuid_object)
    if profile is None:
        return "", 204

    return jsonify({
        "id": profile.uuid.hex,
        "name": profile.name,
        "properties": [
            {
                "name": "textures",  # Who puts a "name" field in a list member? Just make a dict!
                "value": b64encode(dumps(profile.get_texture_data(textures_host)).encode("utf-8")).decode("utf-8"),
                # "signature": ""  # todo?
            }
        ]
    }), 200
