import argparse

from flask import Flask, request

import handler.authserver.authenticate
import handler.authserver.refresh
import handler.authserver.validate
import handler.authserver.signout
import handler.authserver.invalidate
import handler.error

parser = argparse.ArgumentParser()
parser.add_argument("host")
parser.add_argument("-p", "--port", default=80, type=int)
parser.add_argument("-d", "--debug", action="store_true")

args = parser.parse_args()


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8*1024  # 8 kB


@app.errorhandler(404)
def http_404(e):
    return handler.error.http_error_404()


@app.errorhandler(405)
def http_405(e):
    return handler.error.http_error_405()


# @app.errorhandler(500)
# def http_500(e):
#     return handler.error.unhandled_server_error_500()


@app.route("/authenticate", methods=["POST"])
def http_authenticate():
    return handler.authserver.authenticate.json_and_response_code(request)


@app.route("/refresh", methods=["POST"])
def http_refresh():
    return handler.authserver.refresh.json_and_response_code(request)


@app.route("/validate", methods=["POST"])
def http_validate():
    return handler.authserver.validate.json_and_response_code(request)


@app.route("/signout", methods=["POST"])
def http_signout():
    return handler.authserver.signout.json_and_response_code(request)


@app.route("/invalidate", methods=["POST"])
def http_invalidate():
    return handler.authserver.invalidate.json_and_response_code(request)


app.run(host=args.host, port=args.port, debug=args.debug)
