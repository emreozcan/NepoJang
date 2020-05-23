import argparse

from pony.orm import db_session
from pony.orm.core import desc

from db import Profile, ProfileNameEvent


@db_session
def call(program, argv):
    parser = argparse.ArgumentParser(prog=program)

    parser.add_argument("dbid", help="DBID of profile", type=int)
    parser.add_argument("--unix", help="show timestamps as integer", action="store_true")

    args = parser.parse_args(argv)

    profile: Profile = Profile.get(id=args.dbid)
    if profile is None:
        print("No profile matches that DBID!")
        exit(1)

    print(f"History of {profile}")
    print(f"Current name styles: {profile.name}, {profile.name_upper}, {profile.name_lower}")

    for event in profile.profile_name_events.order_by(desc(ProfileNameEvent.active_from)):
        if args.unix:
            print(event.repr_timestamp())
        else:
            print(event)
