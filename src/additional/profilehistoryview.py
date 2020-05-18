import argparse

from pony.orm import db_session
from pony.orm.core import desc

from db import Profile, ProfileNameEvent


@db_session
def call(program, argv):
    parser = argparse.ArgumentParser(prog=program)

    parser.add_argument("dbid", help="DBID of profile", type=int)

    args = parser.parse_args(argv)

    profile = Profile.get(id=args.dbid)
    if profile is None:
        print("No account matches that DBID!")
        exit(1)

    print(f"History of {profile}")
    print(f"Name styles: {profile.name}, {profile.name_upper}, {profile.name_lower}")

    for event in profile.profile_name_events.order_by(desc(ProfileNameEvent.active_from)):
        if event.is_initial_name:
            print(f"Initial name @ {event.active_from}: {event.name}, {event.name_upper}, {event.name_lower}")
        else:
            print(f"Changed name @ {event.active_from}: {event.name}, {event.name_upper}, {event.name_lower}")
