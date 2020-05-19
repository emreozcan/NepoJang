import argparse
from datetime import datetime

from pony.orm import db_session

from db import Profile


@db_session
def call(program, argv):
    parser = argparse.ArgumentParser(prog=program)

    parser.add_argument("dbid", help="DBID of profile", type=int)
    parser.add_argument("timestamp", help="timestamp", type=int)

    args = parser.parse_args(argv)

    profile: Profile = Profile.get(id=args.dbid)
    if profile is None:
        print("No profile matches that DBID!")
        exit(1)

    try:
        event = profile.get_active_name_event_at(datetime.utcfromtimestamp(args.timestamp))
    except OSError:
        print("Invalid timestamp.")
        exit(1)

    if event is None:
        print("This profile didn't have a name at that time.")
        exit(1)

    print(event)
