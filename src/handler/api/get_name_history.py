from uuid import UUID

from flask import jsonify
from pony.orm import db_session, desc

from db import Profile, ProfileNameEvent


@db_session
def json_and_response_code(uuid):
    if len(uuid) != 32:
        return "", 204

    try:
        uuid_object = UUID(uuid)
    except ValueError:
        return "", 204

    profile = Profile.get(uuid=uuid_object)

    if profile is None:
        return "", 204

    history = []

    for event in profile.profile_name_events.order_by(desc(ProfileNameEvent.active_from)):
        event: ProfileNameEvent
        if event.is_initial_name:
            history.append({
                "name": event.name
            })
        else:
            history.append({
                "name": event.name,
                "changedToAt": int(event.active_from.timestamp())
            })

    return jsonify(history), 200
