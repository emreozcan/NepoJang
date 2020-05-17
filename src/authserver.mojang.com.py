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
def _404(e):
    return handler.authserver.xerror_404.xerror_404()


@app.errorhandler(405)
def _405(e):
    return handler.authserver.xerror_405.xerror_405()


@app.route("/authenticate", methods=["POST"])
def authenticate():
    return handler.authserver.authenticate.authenticate(request)


app.run(host=args.host, port=args.port, debug=args.debug)
