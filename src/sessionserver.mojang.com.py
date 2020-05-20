import argparse

from flask import Flask, request

import handler.sessionserver.get_skin_cape
import handler.error

parser = argparse.ArgumentParser()
parser.add_argument("host")
parser.add_argument("-p", "--port", default=80, type=int)
parser.add_argument("-d", "--debug", action="store_true")

args = parser.parse_args()


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16*1024  # 16 kB


@app.errorhandler(404)
def http_404(e):
    return handler.error.http_error_404()


@app.errorhandler(405)
def http_405(e):
    return handler.error.http_error_405()


# @app.errorhandler(500)
# def http_500(e):
#     return handler.error.unhandled_server_error_500()


@app.route("/session/minecraft/profile/<uuid>", methods=["GET"])
def http_get_name_past_owner(uuid):
    return handler.sessionserver.get_skin_cape.json_and_response_code(request, uuid)


@app.route("/blockedservers", methods=["GET"])
def http_get_blocked_servers():
    return "", 200


app.run(host=args.host, port=args.port, debug=args.debug)
