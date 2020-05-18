import argparse
from datetime import datetime
from uuid import uuid4, UUID

from pony.orm import db_session, commit

from db import Account, Profile, ProfileNameEvent


@db_session
def call(program, argv):
    parser = argparse.ArgumentParser(prog=program)

    parser.add_argument("dbid", help="new profile's account DBID", type=int)
    parser.add_argument("name", help="new profile's username")
    parser.add_argument("agent", help="new profile's agent")
    parser.add_argument("-u", "--uuid",  help="new profile's UUID", type=UUID)

    args = parser.parse_args(argv)

    input_uuid = args.uuid if args.uuid is not None else uuid4()

    account = Account.get(id=args.dbid)
    if account is None:
        print("No account matches that DBID!")
        exit(1)

    if account.profiles.count() != 0:
        print(f"Account already has a profile! ({list(account.profiles)[0]})")
        exit(1)

    profile = Profile(
        uuid=input_uuid,
        agent=args.agent,
        account=account,
        name=args.name,
        name_upper=args.name.upper(),
        name_lower=args.name.lower()
    )

    first_name_event = ProfileNameEvent(
        profile=profile,
        active_from=datetime.utcnow(),
        is_initial_name=True,
        name=args.name,
        name_upper=args.name.upper(),
        name_lower=args.name.lower()
    )

    try:
        commit()
    except Exception as e:
        print(str(e))
        exit(1)

    print(profile)
    print(first_name_event)
