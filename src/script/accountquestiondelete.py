import argparse

from pony.orm import db_session

from db import SecurityQuestion


@db_session
def call(program, argv):
    parser = argparse.ArgumentParser(prog=program)

    parser.add_argument("dbid", help="security question dbid", type=int)

    args = parser.parse_args(argv)

    question = SecurityQuestion.get(id=args.dbid)
    if question is None:
        print("There is no question with this DBID.")
        exit(1)

    question.delete()
