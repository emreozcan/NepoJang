from flask import Flask, request
import argparse

import handler.authserver.authenticate
import handler.authserver.xerror_404
import handler.authserver.xerror_405

parser = argparse.ArgumentParser()
parser.add_argument("host")
parser.add_argument("-p", "--port", default=80, type=int)
parser.add_argument("-d", "--debug", action="store_true")

args = parser.parse_args()


app = Flask(__name__)


@app.errorhandler(404)
def http_404(e):
    return handler.authserver.xerror_404.json_and_response_code()


@app.errorhandler(405)
def http_405(e):
    return handler.authserver.xerror_405.json_and_response_code()


@app.route("/authenticate", methods=["POST"])
def http_authenticate():
    return handler.authserver.authenticate.json_and_response_code(request)


app.run(host=args.host, port=args.port, debug=args.debug)
