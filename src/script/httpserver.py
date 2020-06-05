from argparse import ArgumentParser

from flask import Flask, request

import handler.textures.get_texture
import handler.error


def call(program, argv):
    parser = ArgumentParser(prog=program)

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

    @app.route("/texture/<name>", methods=["GET"], host=args.textures_host)
    def http_get_texture(name):
        return handler.textures.get_texture.json_and_response_code(request, name)

    app.run(host=args.textures_host, port=args.port, debug=args.debug, threaded=args.threaded)
