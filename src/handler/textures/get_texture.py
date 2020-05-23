from flask import send_file
from pony.orm import db_session

from paths import TEXTURES_ROOT


@db_session
def json_and_response_code(request, name):
    for group in [sdir for sdir in TEXTURES_ROOT.iterdir() if sdir.is_dir()]:
        file = group.joinpath(name)
        if file.exists():
            return send_file(file, mimetype="image/png")
