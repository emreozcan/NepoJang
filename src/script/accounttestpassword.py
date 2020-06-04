import argparse

from pony.orm import db_session

from db import Account
from util.auth import password_compare


@db_session
def call(program, argv):
    parser = argparse.ArgumentParser(prog=program)

    parser.add_argument("dbid", help="DBID of account", type=int)
    parser.add_argument("password", help="password to test")

    args = parser.parse_args(argv)

    account: Account = Account.get(id=args.dbid)
    if account is None:
        print("No account matches that DBID!")
        exit(1)

    print(password_compare(args.password, account.password))
