from datetime import datetime
from uuid import UUID
from pony.orm import *


set_sql_debug(True)
db = Database()


class Account(db.Entity):
    id = PrimaryKey(int, auto=True)
    uuid = Required(UUID, unique=True)
    username = Required(str, unique=True)  # login information, or email
    password = Required(str)  # hashed password
    profiles = Set('Profile')
    client_tokens = Set('ClientToken')
    access_tokens = Set('AccessToken')


class Profile(db.Entity):
    id = PrimaryKey(int, auto=True)
    uuid = Required(UUID, unique=True)
    name = Required(str, unique=True)  # ign
    account = Required(Account)
    access_tokens = Set('AccessToken')


class ClientToken(db.Entity):
    id = PrimaryKey(int, auto=True)
    uuid = Required(UUID, unique=True)
    account = Required(Account)  # which account does this client token authorize
    access_tokens = Set('AccessToken')


class AccessToken(db.Entity):
    id = PrimaryKey(int, auto=True)
    uuid = Required(UUID, unique=True)
    issuer = Required(str)
    created_utc = Required(datetime)
    expiry_utc = Required(datetime)
    authentication_valid = Required(bool)
    account = Required(Account)
    profile = Required(Profile)  # which profile can this access token represents
    client_token = Required(ClientToken)  # client that created this access token


db.bind(provider="sqlite", filename="tmp.sqlite3", create_db=True)
db.generate_mapping(create_tables=True)
