import argparse
import re

from pony.orm import db_session

from db import Profile, Account


@db_session
def call(program, argv):
    parser = argparse.ArgumentParser(prog=program)

    parser.add_argument("-o", "--owner", help="owner account's DBID", type=int)
    parser.add_argument("-n", "--name", help="name regex", metavar="REGEX")
    parser.add_argument("-a", "--agent", help="agent regex", metavar="REGEX")
    parser.add_argument("-u", "--uuid", help="UUID regex no dashes", metavar="REGEX")
    parser.add_argument("-igt", "--id-gt", help="DBID is greater than X", metavar="X", type=int)
    parser.add_argument("-ilt", "--id-lt", help="DBID is less than X", metavar="X", type=int)
    parser.add_argument("-x", "--max", help="maximum entries printed", metavar="X", type=int)

    args = parser.parse_args(argv)

    name_pattern = re.compile(args.name if args.name is not None else ".*")
    agent_pattern = re.compile(args.agent if args.agent is not None else ".*")
    uuid_pattern = re.compile(args.uuid if args.uuid is not None else ".*")

    profiles = Profile.select()

    if args.owner is not None:
        expected_owner: Account = Account.get(id=args.owner)
        if expected_owner is None:
            print("This owner DBID doesn't match any accounts!")
            exit(1)

    printed_count = 0
    for profile in profiles:
        if args.owner is not None:
            if profile.account != expected_owner:
                continue
        if name_pattern.fullmatch(profile.name) is None:
            continue
        if agent_pattern.fullmatch(profile.agent) is None:
            continue
        if uuid_pattern.fullmatch(profile.uuid.hex) is None:
            continue
        if args.id_gt is not None and not profile.id > args.id_gt:
            continue
        if args.id_lt is not None and not profile.id < args.id_lt:
            continue
        printed_count += 1
        print(str(profile))
        if args.max is not None and printed_count >= args.max:
            break
