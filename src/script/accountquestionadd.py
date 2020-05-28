import argparse

from pony.orm import db_session, commit

from constant.security_questions import questions
from db import Account


@db_session
def call(program, argv):
    parser = argparse.ArgumentParser(prog=program)

    parser.add_argument("dbid", help="account dbid", type=int)
    parser.add_argument("qid", help="question id", type=int)
    parser.add_argument("answer", help="question answer")

    args = parser.parse_args(argv)

    account = Account.get(id=args.dbid)
    if account is None:
        print("There is no account with this DBID.")
        exit(1)

    if args.qid not in questions:
        print("Invalid question id.")
        exit(1)

    question = account.add_answer(question_id=args.qid, answer=args.answer)

    commit()

    print(question)
