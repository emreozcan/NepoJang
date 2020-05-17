from datetime import datetime
from uuid import UUID, uuid4
from pony.orm import *


set_sql_debug(True)
db = Database()


class Account(db.Entity):
    id = PrimaryKey(int, auto=True)
    uuid = Required(UUID, unique=True, auto=uuid4)
    username = Required(str, unique=True)  # login information, or email
    password = Required(str)  # hashed password
    profiles = Set('Profile')
    client_tokens = Set('ClientToken')
    access_tokens = Set('AccessToken')

    def __repr__(self):
        return f"{self.username} ({str(self.uuid)})"


class Profile(db.Entity):
    id = PrimaryKey(int, auto=True)
    uuid = Required(UUID, unique=True, auto=uuid4)
    agent = Required(str)
    name = Required(str, unique=True)  # ign
    account = Required(Account)
    access_tokens = Set('AccessToken')

    def __repr__(self):
        return f"{self.name} ({str(self.uuid)})"


class ClientToken(db.Entity):
    id = PrimaryKey(int, auto=True)
    uuid = Required(UUID, unique=True, auto=uuid4)
    account = Required(Account)  # which account does this client token authorize
    access_tokens = Set('AccessToken')


class AccessToken(db.Entity):
    id = PrimaryKey(int, auto=True)
    uuid = Required(UUID, unique=True, auto=uuid4)
    issuer = Required(str)
    created_utc = Required(datetime)
    expiry_utc = Required(datetime)
    authentication_valid = Required(bool)  # is access token valid for authenticating with game servers
    account = Required(Account)
    client_token = Required(ClientToken)  # client that created this access token
    profile = Optional(Profile)  # which profile can this access token grants access to


db.bind(provider="sqlite", filename="tmp.sqlite3", create_db=True)
db.generate_mapping(create_tables=True)
