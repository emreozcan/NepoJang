import argparse
from uuid import UUID, uuid4

from pony.orm import db_session
from pony.orm.core import commit

from db import Account
from util.auth import password_hash


@db_session
def call(program, argv):
    parser = argparse.ArgumentParser(prog=program)

    parser.add_argument("dbid", help="DBID of account", type=int)

    uuids = parser.add_mutually_exclusive_group()
    uuids.add_argument("-u", "--uuid", help="change account UUID", type=UUID)
    uuids.add_argument("-ru", "--random-uuid", help="refresh account UUID", action="store_true")

    parser.add_argument("-n", "--username", help="change account username")
    parser.add_argument("-p", "--password", help="change account password")
    parser.add_argument("--delete", help="delete this account", action="store_true")

    args = parser.parse_args(argv)

    account: Account = Account.get(id=args.dbid)
    if account is None:
        print("No account matches that DBID!")
        exit(1)

    if args.uuid is not None:
        account.uuid = args.uuid
    if args.random_uuid:
        account.uuid = uuid4()
    if args.username is not None:
        account.username = args.username
    if args.password is not None:
        account.password = password_hash(args.password)
    if args.delete:
        account.delete()

    try:
        commit()
    except Exception as e:
        print(e)
        exit(1)

    if not args.delete:
        print(str(account))
