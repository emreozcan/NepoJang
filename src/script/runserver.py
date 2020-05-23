import argparse

from flask import Flask, request

import handler.api.get_name_past_owner
import handler.api.get_name_history
import handler.api.get_uuids
import handler.api.change_skin
import handler.authserver.authenticate
import handler.authserver.refresh
import handler.authserver.validate
import handler.authserver.signout
import handler.authserver.invalidate
import handler.sessionserver.get_skin_cape
import handler.textures.get_texture
import handler.error


def call(program, argv):
    parser = argparse.ArgumentParser(prog=program)
    parser.add_argument("api_host")
    parser.add_argument("authserver_host")
    parser.add_argument("sessionserver_host")
    parser.add_argument("textures_host")
    parser.add_argument("-p", "--port", default=80, type=int)
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-t", "--threaded", action="store_true")

    args = parser.parse_args(argv)

    app = Flask(__name__, host_matching=True, static_host=args.textures_host)
    app.config.update(
        MAX_CONTENT_LENGTH=16 * 1024,  # 16 kB
    )

    # region Common
    @app.errorhandler(404)
    def http_404(e):
        return handler.error.http_error_404()

    @app.errorhandler(405)
    def http_405(e):
        return handler.error.http_error_405()

    # @app.errorhandler(500)
    # def http_500(e):
    #     return handler.error.unhandled_server_error_500()
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
    # endregion

    # region Textures
    @app.route("/texture/<name>", methods=["GET"], host=args.textures_host)
    def http_get_texture(name):
        return handler.textures.get_texture.json_and_response_code(request, name)
    # endregion

    app.run(host=args.api_host, port=args.port, debug=args.debug, threaded=args.threaded)