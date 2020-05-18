from datetime import datetime
from uuid import UUID, uuid4

from pony.orm import set_sql_debug, Database, PrimaryKey, Required, Set, Optional

set_sql_debug(False)
db = Database()


class Account(db.Entity):
    id = PrimaryKey(int, auto=True)
    uuid = Required(UUID, unique=True, auto=uuid4)
    username = Required(str, unique=True)  # login information, or email
    password = Required(str)  # hashed password
    profiles = Set('Profile')  # official Mojang api supports 1 profile but multiple may be supported in the future
    client_tokens = Set('ClientToken')
    access_tokens = Set('AccessToken')

    def __repr__(self):
        return f"{self.id}, {self.username}, {self.uuid}"

    def __str__(self):
        return repr(self)


class Profile(db.Entity):
    id = PrimaryKey(int, auto=True)
    uuid = Required(UUID, unique=True, auto=uuid4)
    agent = Required(str)
    account = Required(Account)
    access_tokens = Set('AccessToken')
    profile_name_events = Set('ProfileNameEvent')
    name = Required(str, unique=True)  # ign
    name_upper = Required(str, unique=True)
    name_lower = Required(str, unique=True)

    def __repr__(self):
        return f"{self.id}, {self.name}, {self.uuid} (for {self.agent}) -of> {self.account.id}, {self.account.username}"

    def __str__(self):
        return repr(self)


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


class ProfileNameEvent(db.Entity):
    id = PrimaryKey(int, auto=True)
    profile = Required(Profile)
    active_from = Required(datetime)
    is_initial_name = Required(bool)
    name = Required(str)
    name_upper = Required(str)
    name_lower = Required(str)

    def __repr__(self):
        if self.is_initial_name:
            return f"Profile ({self.profile.id}, {self.profile.name}) created with: {self.name}"
        return f"Profile ({self.profile.id}, {self.profile.name}), @ {self.active_from}: {self.name}"

    def __str__(self):
        return repr(self)


db.bind(provider="sqlite", filename="tmp.sqlite3", create_db=True)
db.generate_mapping(create_tables=True)
