import argparse

from pony.orm import db_session

from db import Account


@db_session
def call(program, argv):
    parser = argparse.ArgumentParser(prog=program)

    parser.add_argument("dbid", help="account dbid", type=int)

    args = parser.parse_args(argv)

    account = Account.get(id=args.dbid)
    if account is None:
        print("There is no account with this DBID.")
        exit(1)

    for question in account.security_questions:
        print(question)
