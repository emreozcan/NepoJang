from flask import jsonify

services = {
    "minecraft.net": "red",
    "session.minecraft.net": "red",
    "account.mojang.com": "red",
    "auth.mojang.com": "green",
    "skins.minecraft.net": "red",
    "authserver.mojang.com": "green",
    "sessionserver.mojang.com": "green",
    "api.mojang.com": "green",
    "textures.minecraft.net": "green",
    "mojang.com": "green"
}


def json_and_response_code(request):
    service = request.args.get("service")
    if service is None:
        return jsonify([{s[0]: s[1]} for s in services.items()]), 200

    if service not in services:
        return f"Unknown service: {service}", 200

    return jsonify({service: services[service]}), 200
