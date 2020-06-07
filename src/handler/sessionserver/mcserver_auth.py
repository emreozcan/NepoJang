from uuid import UUID

from flask import Request, jsonify
from pony.orm import db_session

from constant.error import NULL_ACCESS_TOKEN, NULL_MESSAGE, INVALID_UUID, INVALID_TOKEN, BAD_REQUEST, \
    MCSERVER_DIFFERENT_IP, MCSERVER_INVALID_SESSION, MCSERVER_INVALID_PROFILE
from db import AccessToken, Profile, MCServerSession
from util.decorators import require_json
from util.public_profile_details import get_public_profile_details

BARE_BAD_REQUEST = "", 400


@db_session
@require_json
def join_mcclient(request: Request):
    if "accessToken" not in request.json:
        # May be inconsistent with official API
        return NULL_ACCESS_TOKEN.dual

    if "selectedProfile" not in request.json or "serverId" not in request.json:
        # May be inconsistent with official API
        return NULL_MESSAGE.dual

    access_token = AccessToken.from_token(request.json["accessToken"])
    if access_token is None:
        # May be inconsistent with official API
        return INVALID_TOKEN.dual

    try:
        profile = Profile.get(lambda x: x.uuid == UUID(request.json["selectedProfile"]))
    except ValueError:
        # May be inconsistent with official API
        return INVALID_UUID.dual

    if access_token.profile != profile:
        # May be inconsistent with official API
        return INVALID_TOKEN.dual

    session = MCServerSession.get(lambda x:
                                  x.profile == profile
                                  and x.client_side_ip == request.remote_addr
                                  and x.server_hash == request.json["serverId"])

    if session is None:
        MCServerSession.select(lambda x: x.profile == profile).delete()
        MCServerSession(
            profile=profile,
            client_side_ip=request.remote_addr,
            server_hash=request.json["serverId"],
        )

    return "", 204


@db_session
def join_mcserver(request, textures_host):
    username, server_hash, ip = request.args.get("username"), request.args.get("serverId"), request.args.get("ip")
    if username is None or server_hash is None:
        # May be inconsistent with official API
        return NULL_MESSAGE.dual

    profile = Profile.get_profile_with_name(username)
    if profile is None:
        # May be inconsistent with official API
        return MCSERVER_INVALID_PROFILE.dual

    session = MCServerSession.get(lambda x:
                                  x.profile == profile
                                  and x.server_hash == server_hash)

    if session is None:
        # May be inconsistent with official API
        return MCSERVER_INVALID_SESSION.dual

    if ip is not None and session.client_side_ip != ip:
        # May be inconsistent with official API
        return MCSERVER_DIFFERENT_IP.dual

    session.delete()

    return jsonify(get_public_profile_details(profile, False, textures_host)), 200
