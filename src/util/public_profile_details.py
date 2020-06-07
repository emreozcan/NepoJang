from base64 import b64encode
from json import dumps

from db import Profile


def get_public_profile_details(profile: Profile, unsigned: bool, textures_host: str) -> dict:
    data = {
        "id": profile.uuid.hex,
        "name": profile.name,
        "properties": [
            {
                "name": "textures",  # Who puts a "name" field in a list member? Just make a dict!
                "value": b64encode(dumps(profile.get_texture_data(textures_host)).encode("utf-8")).decode("utf-8"),
                # "signature": ""  # todo?
            }
        ]
    }

    if not unsigned:
        pass  # todo?

    return data
