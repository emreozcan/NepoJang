import argparse
from datetime import datetime

from pony.orm import db_session
from pony.orm.core import commit

from db import Profile, ProfileNameEvent


@db_session
def call(program, argv):
    parser = argparse.ArgumentParser(prog=program)

    parser.add_argument("dbid", help="DBID of profile", type=int)
    parser.add_argument("name", help="new name of profile")

    args = parser.parse_args(argv)

    profile = Profile.get(id=args.dbid)
    if profile is None:
        print("No account matches that DBID!")
        exit(1)

    profile.name = args.name
    profile.name_upper = args.name.upper()
    profile.name_lower = args.name.lower()
    name_event = ProfileNameEvent(
        profile=profile,
        active_from=datetime.utcnow(),
        is_initial_name=False,
        name=args.name,
        name_upper=args.name.upper(),
        name_lower=args.name.lower()
    )

    try:
        commit()
    except Exception as e:
        print(e)
        exit(1)

    print(profile)
    print(name_event)
