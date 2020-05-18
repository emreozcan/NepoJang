import argparse
import re

from pony.orm import db_session

from db import Account


@db_session
def call(program, argv):
    parser = argparse.ArgumentParser(prog=program)

    parser.add_argument("-n", "--username", help="username regex", metavar="REGEX")
    parser.add_argument("-u", "--uuid", help="UUID regex no dashes", metavar="REGEX")
    parser.add_argument("-igt", "--id-gt", help="DBID is greater than X", metavar="X", type=int)
    parser.add_argument("-ilt", "--id-lt", help="DBID is less than X", metavar="X", type=int)
    parser.add_argument("-x", "--max", help="maximum entries printed", metavar="X", type=int)

    args = parser.parse_args(argv)

    username_pattern = re.compile(args.username if args.username is not None else ".*")
    uuid_pattern = re.compile(args.uuid if args.uuid is not None else ".*")

    accounts = Account.select()

    printed_count = 0
    for account in accounts:
        if username_pattern.fullmatch(account.username) is None:
            continue
        if uuid_pattern.fullmatch(account.uuid.hex) is None:
            continue
        if args.id_gt is not None and not account.id > args.id_gt:
            continue
        if args.id_lt is not None and not account.id < args.id_lt:
            continue
        printed_count += 1
        print(str(account))
        if args.max is not None and printed_count >= args.max:
            break
