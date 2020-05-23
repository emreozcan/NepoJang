import argparse
from uuid import uuid4, UUID

from pony.orm import db_session, commit

from db import Account
from password import password_hash


@db_session
def call(program, argv):
    parser = argparse.ArgumentParser(prog=program)

    parser.add_argument("username", help="new account's username")
    parser.add_argument("password", help="new account's password")
    parser.add_argument("-u", "--uuid",  help="new account's UUID", type=UUID)

    args = parser.parse_args(argv)

    input_uuid = args.uuid if args.uuid is not None else uuid4()

    account = Account(
        username=args.username,
        password=password_hash(args.password),
        uuid=input_uuid
    )

    try:
        commit()
    except Exception as e:
        print(e)
        exit(1)

    print(str(account))
