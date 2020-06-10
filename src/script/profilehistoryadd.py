import argparse

from pony.orm import db_session
from pony.orm.core import commit

from db import Profile


@db_session
def call(program, argv):
    parser = argparse.ArgumentParser(prog=program)

    parser.add_argument("dbid", help="DBID of profile", type=int)
    parser.add_argument("name", help="new name of profile")

    parser.add_argument("--bypass-wait", help="do not wait 30 days between name changes", action="store_true")
    parser.add_argument("--bypass-lock", help="do not wait 37 days for profile name to unlock", action="store_true")

    args = parser.parse_args(argv)

    profile: Profile = Profile.get(id=args.dbid)
    if profile is None:
        print("No profile matches that DBID!")
        exit(1)

    if not (args.bypass_wait or profile.can_change_name()):
        print(f"Cannot change name until {profile.time_of_next_name_change()}. Wait {profile.time_to_name_change()}.")
        exit(1)

    if not (args.bypass_lock or profile.is_name_available_for_change(args.name)):
        print("Name not available.")
        exit(1)

    profile.change_name(args.name)

    try:
        commit()
    except Exception as e:
        print(e)
        exit(1)

    print(profile)
