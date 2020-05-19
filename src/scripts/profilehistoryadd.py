import argparse

from pony.orm import db_session
from pony.orm.core import commit

from db import Profile, ProfileNameEvent


@db_session
def call(program, argv):
    parser = argparse.ArgumentParser(prog=program)

    parser.add_argument("dbid", help="DBID of profile", type=int)
    parser.add_argument("name", help="new name of profile")

    args = parser.parse_args(argv)

    profile: Profile = Profile.get(id=args.dbid)
    if profile is None:
        print("No profile matches that DBID!")
        exit(1)

    if not profile.can_change_name_to(args.name):
        print("Name not available.")
        exit(1)

    profile.attempt_name_change(args.name)

    try:
        commit()
    except Exception as e:
        print(e)
        exit(1)

    print(profile)
