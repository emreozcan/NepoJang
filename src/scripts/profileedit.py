import argparse
from uuid import UUID, uuid4

from pony.orm import db_session
from pony.orm.core import commit

from db import Profile


@db_session
def call(program, argv):
    parser = argparse.ArgumentParser(prog=program)

    parser.add_argument("dbid", help="DBID of profile", type=int)

    uuids = parser.add_mutually_exclusive_group()
    uuids.add_argument("-u", "--uuid", help="change profile UUID", type=UUID)
    uuids.add_argument("-ru", "--random-uuid", help="refresh profile UUID", action="store_true")

    parser.add_argument("-a", "--agent", help="change profile agent")
    parser.add_argument("--delete", help="delete this profile", action="store_true")

    args = parser.parse_args(argv)

    profile: Profile = Profile.get(id=args.dbid)
    if profile is None:
        print("No profile matches that DBID!")
        exit(1)

    if args.uuid is not None:
        profile.uuid = args.uuid
    if args.random_uuid:
        profile.uuid = uuid4()
    if args.agent is not None:
        profile.agent = args.agent
    if args.delete:
        profile.delete()

    try:
        commit()
    except Exception as e:
        print(e)
        exit(1)

    if not args.delete:
        print(str(profile))
