import argparse

from flask import Flask, request

import handler.api.get_name_past_owner
import handler.api.get_name_history
import handler.api.get_uuids
import handler.api.change_skin
import handler.api.security
import handler.authserver.authenticate
import handler.authserver.refresh
import handler.authserver.validate
import handler.authserver.signout
import handler.authserver.invalidate
import handler.sessionserver.get_skin_cape
import handler.sessionserver.mcserver_auth
import handler.status.check
import handler.error

from paths import HTTP_PRIVATE_KEY_PATH, HTTP_CERTIFICATE_PATH, setup as setup_paths
from util.crypto.httpcert import create_and_write_http_keys, create_and_write_csr, issue_and_write_certificate
from util.crypto.rootca import create_and_write_root_certificate


def call(program, argv):
    parser = argparse.ArgumentParser(prog=program)
    parser.add_argument("api_host", help="Also used for IP and static host")
    parser.add_argument("authserver_host")
    parser.add_argument("sessionserver_host")
    parser.add_argument("textures_host")
    parser.add_argument("status_host")
    parser.add_argument("-p", "--port", default=443, type=int)
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-t", "--threaded", action="store_true")

    args = parser.parse_args(argv)

    app = Flask(__name__, host_matching=True, static_host=args.api_host)
    app.config.update(
        MAX_CONTENT_LENGTH=16 * 1024,  # 16 kB
    )

    # region Common
    @app.errorhandler(400)
    def http_400(_):
        return handler.error.http_error_400()

    @app.errorhandler(404)
    def http_404(_):
        return handler.error.http_error_404()

    @app.errorhandler(405)
    def http_405(_):
        return handler.error.http_error_405()

    @app.errorhandler(500)
    def http_500(_):
        return handler.error.unhandled_server_error_500()
    # endregion

    # region API
    @app.route("/users/profiles/minecraft/<username>", methods=["GET"], host=args.api_host)
    def http_get_name_past_owner(username):
        return handler.api.get_name_past_owner.json_and_response_code(request, username)

    @app.route("/user/profiles/<uuid>/names", methods=["GET"], host=args.api_host)
    def http_get_name_history(uuid):
        return handler.api.get_name_history.json_and_response_code(uuid)

    @app.route("/profiles/minecraft", methods=["POST"], host=args.api_host)
    def http_get_uuids():
        return handler.api.get_uuids.json_and_response_code(request)

    @app.route("/user/profile/<uuid>/skin", methods=["POST", "PUT", "DELETE"], host=args.api_host)
    def http_change_skin(uuid):
        return handler.api.change_skin.json_and_response_code(request, uuid)

    @app.route("/user/security/location", methods=["GET", "POST"], host=args.api_host)
    def http_security_location():
        return handler.api.security.location(request)

    @app.route("/user/security/challenges", methods=["GET"], host=args.api_host)
    def http_security_challenges():
        return handler.api.security.list_challenges(request)
    # endregion

    # region Authserver
    @app.route("/authenticate", methods=["POST"], host=args.authserver_host)
    def http_authenticate():
        return handler.authserver.authenticate.json_and_response_code(request)

    @app.route("/refresh", methods=["POST"], host=args.authserver_host)
    def http_refresh():
        return handler.authserver.refresh.json_and_response_code(request)

    @app.route("/validate", methods=["POST"], host=args.authserver_host)
    def http_validate():
        return handler.authserver.validate.json_and_response_code(request)

    @app.route("/signout", methods=["POST"], host=args.authserver_host)
    def http_signout():
        return handler.authserver.signout.json_and_response_code(request)

    @app.route("/invalidate", methods=["POST"], host=args.authserver_host)
    def http_invalidate():
        return handler.authserver.invalidate.json_and_response_code(request)
    # endregion

    # region Sessionserver
    @app.route("/session/minecraft/profile/<uuid>", methods=["GET"], host=args.sessionserver_host)
    def http_get_skin_cape(uuid):
        return handler.sessionserver.get_skin_cape.json_and_response_code(request, uuid, args.textures_host)

    @app.route("/blockedservers", methods=["GET"], host=args.sessionserver_host)
    def http_get_blocked_servers():
        return "", 200

    @app.route("/session/minecraft/join", methods=["POST"], host=args.sessionserver_host)
    def http_mcserver_auth_clientside():
        return handler.sessionserver.mcserver_auth.join_mcclient(request)

    @app.route("/session/minecraft/hasJoined", methods=["GET"], host=args.sessionserver_host)
    def http_mcserver_auth_serverside():
        return handler.sessionserver.mcserver_auth.join_mcserver(request, args.textures_host)
    # endregion

    # region Status
    @app.route("/check", methods=["GET"], host=args.status_host)
    def http_get_status():
        return handler.status.check.json_and_response_code(request)
    # endregion

    setup_paths()

    create_and_write_root_certificate(overwrite=False)
    http_certificate_private_key = create_and_write_http_keys(overwrite=False)
    http_certificate_request = create_and_write_csr(
        http_key=http_certificate_private_key,
        domains=[
            args.api_host,
            args.authserver_host,
            args.sessionserver_host,
            args.status_host,
        ],
        overwrite=True
    )
    issue_and_write_certificate(http_certificate_request, overwrite=True)

    context = (str(HTTP_CERTIFICATE_PATH), str(HTTP_PRIVATE_KEY_PATH))
    app.run(host=args.api_host, port=args.port, debug=args.debug, threaded=args.threaded, ssl_context=context)
