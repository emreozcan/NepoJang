from argparse import ArgumentParser
from io import BytesIO
from pathlib import Path

from PIL import Image, UnidentifiedImageError
from pony.orm import db_session
from pony.orm.core import commit
from requests import get

from constant.error import INVALID_IMAGE, INVALID_SKIN
from db import Profile


@db_session
def call(program, argv):
    parser = ArgumentParser(prog=program)

    parser.add_argument("dbid", help="DBID of profile", type=int)

    sources = parser.add_mutually_exclusive_group(required=True)
    sources.add_argument("-u", "--url", help="url of skin", dest="url")
    sources.add_argument("-f", help="file path of skin", dest="path")
    sources.add_argument("--delete", help="reset profile skin", action="store_true")

    parser.add_argument("--slim", help="slim model", action="store_true")

    args = parser.parse_args(argv)

    profile: Profile = Profile.get(id=args.dbid)
    if profile is None:
        print("No profile matches that DBID!")
        exit(1)

    if args.url is not None:
        fd = BytesIO(get(args.url).content)
    elif args.path is not None:
        fd = Path(args.path)
    elif not args.delete:
        print("You must specify a file!")
        exit(1)

    if args.delete:
        profile.reset_skin()
    else:
        try:
            image: Image = Image.open(fd)
        except (FileNotFoundError, UnidentifiedImageError, ValueError):
            print(INVALID_IMAGE.message)
            exit(1)

        try:
            profile.update_skin(image, "slim" if args.slim else "")
        except ValueError:
            print(INVALID_SKIN.message)
            exit(1)

    try:
        commit()
    except Exception as e:
        print(e)
        exit(1)

    if not args.delete:
        print(f"Texture name: {profile.profile_skin.name}")
