import argparse
from uuid import uuid4, UUID

from pony.orm import db_session, commit

from db import Account, SecurityQuestion
from password import password_hash


@db_session
def call(program, argv):
    parser = argparse.ArgumentParser(prog=program)

    parser.add_argument("username", help="new account's username")
    parser.add_argument("password", help="new account's password")
    parser.add_argument("q1", help="security question #1 id", type=int)
    parser.add_argument("a1", help="security answer #1")
    parser.add_argument("q2", help="security question #2 id", type=int)
    parser.add_argument("a2", help="security answer #2")
    parser.add_argument("q3", help="security question #3 id", type=int)
    parser.add_argument("a3", help="security answer #3")

    parser.add_argument("-u", "--uuid",  help="new account's UUID", type=UUID)

    args = parser.parse_args(argv)

    input_uuid = args.uuid if args.uuid is not None else uuid4()

    account = Account(
        username=args.username,
        password=password_hash(args.password),
        uuid=input_uuid
    )

    if args.q1 < 1 or args.q1 > 39 or args.q2 < 1 or args.q2 > 39 or args.q3 < 1 or args.q3 > 39:
        print("Question ID must be between 1 and 39.")

    SecurityQuestion(account=account, question_id=args.q1, answer=args.a1)
    SecurityQuestion(account=account, question_id=args.q2, answer=args.a2)
    SecurityQuestion(account=account, question_id=args.q3, answer=args.a3)

    try:
        commit()
    except Exception as e:
        print(e)
        exit(1)

    print(str(account))
