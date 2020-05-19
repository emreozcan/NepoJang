import argparse

from flask import Flask, request

import handler.api.username_and_time_to_uuid
import handler.api.uuid_to_name_history
import handler.api.multiple_usernames_to_uuids
import handler.api.xerror_404
import handler.api.xerror_405

parser = argparse.ArgumentParser()
parser.add_argument("host")
parser.add_argument("-p", "--port", default=80, type=int)
parser.add_argument("-d", "--debug", action="store_true")

args = parser.parse_args()


app = Flask(__name__)


@app.errorhandler(404)
def http_404(e):
    return handler.api.xerror_404.json_and_response_code()


@app.errorhandler(405)
def http_405(e):
    return handler.api.xerror_405.json_and_response_code()


@app.route("/users/profiles/minecraft/<username>", methods=["GET"])
def http_username_and_time_to_uuid(username):
    return handler.api.username_and_time_to_uuid.json_and_response_code(request, username)


@app.route("/user/profiles/<uuid>/names", methods=["GET"])
def http_uuid_to_name_history(uuid):
    return handler.api.uuid_to_name_history.json_and_response_code(uuid)


@app.route("/profiles/minecraft", methods=["POST"])
def http_multple_usernames_to_uuids():
    return handler.api.multiple_usernames_to_uuids.json_and_response_code(request)


app.run(host=args.host, port=args.port, debug=args.debug)
