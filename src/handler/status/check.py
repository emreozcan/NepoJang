from flask import jsonify

from constant.services import API_SERVICES


def json_and_response_code(request):
    service = request.args.get("service")
    if service is None:
        return jsonify([{s[0]: s[1]} for s in API_SERVICES.items()]), 200

    if service not in API_SERVICES:
        return f"Unknown service: {service}", 200

    return jsonify({service: API_SERVICES[service]}), 200
