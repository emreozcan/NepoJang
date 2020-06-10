import argparse
from datetime import datetime

from pony.orm import db_session, desc

from db import Profile, ProfileNameEvent


@db_session
def call(program, argv):
    parser = argparse.ArgumentParser(prog=program)

    parser.add_argument("name", help="profile name")
    parser.add_argument("-t", "--time", help="timestamp of past time", type=int)
    parser.add_argument("--unix", help="show timestamps as integer", action="store_true")

    args = parser.parse_args(argv)

    if args.time is None:
        args.time = datetime.utcnow()

    event = Profile.that_owned_name_at(args.name, args.time)

    print(f"History of {args.name}")

    if event is None:
        print(f"No profile owned that name at {args.time}!")
    else:
        print(f"Owner of {event.name} @ {args.time}: {event.profile}")

    events = ProfileNameEvent.select(lambda x: x.name == args.name
                                     or x.name_upper == args.name.upper()
                                     or x.name_lower == args.name.lower())\
        .order_by(desc(ProfileNameEvent.active_from))

    for old_event in events:
        print(old_event)
