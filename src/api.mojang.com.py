import argparse

from flask import Flask, request

import handler.api.get_name_past_owner
import handler.api.get_name_history
import handler.api.get_uuids
import handler.api.change_skin
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


@app.route("/users/profiles/minecraft/<username>", methods=["GET"])
def http_get_name_past_owner(username):
    return handler.api.get_name_past_owner.json_and_response_code(request, username)


@app.route("/user/profiles/<uuid>/names", methods=["GET"])
def http_get_name_history(uuid):
    return handler.api.get_name_history.json_and_response_code(uuid)


@app.route("/profiles/minecraft", methods=["POST"])
def http_get_uuids():
    return handler.api.get_uuids.json_and_response_code(request)


@app.route("/user/profile/<uuid>/skin", methods=["POST", "PUT", "DELETE"])
def http_change_skin(uuid):
    return handler.api.change_skin.json_and_response_code(request, uuid)


app.run(host=args.host, port=args.port, debug=args.debug)
