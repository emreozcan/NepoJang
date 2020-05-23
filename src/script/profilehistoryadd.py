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

    if not (args.bypass_wait or profile.name_change_is_allowed()):
        print(f"Cannot change name until {profile.name_change_time_until()}. Wait {profile.name_change_wait_delta()}.")
        exit(1)

    if not (args.bypass_lock or profile.name_available_for_change(args.name)):
        print("Name not available.")
        exit(1)

    profile.attempt_name_change(args.name)

    try:
        commit()
    except Exception as e:
        print(e)
        exit(1)

    print(profile)
