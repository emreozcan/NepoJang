from datetime import datetime, timedelta
from uuid import UUID, uuid4

from pony.orm import set_sql_debug, Database, PrimaryKey, Required, Set, Optional, desc

set_sql_debug(False)
db = Database()


class Account(db.Entity):
    id = PrimaryKey(int, auto=True)
    uuid = Required(UUID, unique=True, default=uuid4)
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
    uuid = Required(UUID, unique=True, default=uuid4)
    agent = Required(str)
    account = Required(Account)
    access_tokens = Set('AccessToken')
    profile_name_events = Set('ProfileNameEvent')
    name = Required(str, unique=True)  # ign
    name_upper = Required(str, unique=True, column="name_upper")
    name_lower = Required(str, unique=True, column="name_lower")

    def set_name_and_styles(self, new_name):
        self.name = new_name
        self.name_upper = new_name.upper()
        self.name_lower = new_name.lower()

    def attempt_name_change(self, new_name_attempt):
        self.set_name_and_styles(new_name_attempt)
        ProfileNameEvent(
            profile=self,
            is_initial_name=False,
            name=new_name_attempt
        )

    def get_name_event_at(self, datetime_object: datetime):
        pne = ProfileNameEvent.select(lambda x: x.profile == self and x.active_from < datetime_object)\
            .order_by(desc(ProfileNameEvent.active_from))
        return pne.first()

    def can_change_name_to(self, new_name_attempt) -> bool:
        if Profile.select(lambda profile: profile.name == new_name_attempt and profile != self).exists():
            return False
        if Profile.select(lambda profile: profile.name_upper == new_name_attempt.upper() and profile != self).exists():
            return False
        if Profile.select(lambda profile: profile.name_lower == new_name_attempt.lower() and profile != self).exists():
            return False
        return True

    @staticmethod
    def is_name_available(new_name_attempt) -> bool:
        if Profile.select(lambda profile: profile.name == new_name_attempt).exists():
            return False
        if Profile.select(lambda profile: profile.name_upper == new_name_attempt.upper()).exists():
            return False
        if Profile.select(lambda profile: profile.name_lower == new_name_attempt.lower()).exists():
            return False
        return True

    @staticmethod
    def create_profile_and_history(*args, **kwargs):
        new_profile = Profile(*args, **kwargs)
        ProfileNameEvent(
            profile=new_profile,
            is_initial_name=True,
            name=kwargs["name"]
        )
        return new_profile

    def __init__(self, *args, **kwargs):
        if "name_upper" not in kwargs:
            kwargs["name_upper"] = kwargs["name"].upper()
        if "name_lower" not in kwargs:
            kwargs["name_lower"] = kwargs["name"].lower()
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"{self.id}, {self.name}, {self.uuid} (for {self.agent}) -of> {self.account.id}, {self.account.username}"

    def __str__(self):
        return repr(self)


class ClientToken(db.Entity):
    id = PrimaryKey(int, auto=True)
    uuid = Required(UUID, unique=True, default=uuid4)
    account = Required(Account)  # which account does this client token authorize
    access_tokens = Set('AccessToken')


class AccessToken(db.Entity):
    id = PrimaryKey(int, auto=True)
    uuid = Required(UUID, unique=True, default=uuid4)
    issuer = Required(str, default="Yggdrasil-Auth")
    created_utc = Required(datetime, default=datetime.utcnow)
    expiry_utc = Required(datetime, default=lambda: datetime.utcnow()+timedelta(days=2))
    authentication_valid = Required(bool, default=True)  # is access token valid for authenticating with game servers
    account = Required(Account)
    client_token = Required(ClientToken)  # client that created this access token
    profile = Optional(Profile)  # which profile can this access token grants access to

    def format(self):
        data = {
            "sub": self.account.uuid.hex,
            "yggt": self.uuid.hex,
            "issr": self.issuer,
            "exp": int(self.expiry_utc.timestamp()),
            "iat": int(self.created_utc.timestamp())
        }
        if self.profile:
            data["spr"] = self.profile.uuid.hex
        return data


class ProfileNameEvent(db.Entity):
    id = PrimaryKey(int, auto=True)
    profile = Required(Profile)
    active_from = Required(datetime, default=datetime.utcnow)
    is_initial_name = Required(bool)
    name = Required(str)
    name_upper = Required(str)
    name_lower = Required(str)

    def __init__(self, *args, **kwargs):
        if "name_upper" not in kwargs:
            kwargs["name_upper"] = kwargs["name"].upper()
        if "name_lower" not in kwargs:
            kwargs["name_lower"] = kwargs["name"].lower()
        super().__init__(*args, **kwargs)

    def __repr__(self):
        if self.is_initial_name:
            return f"Profile ({self.profile.id}, {self.profile.name}) created with: {self.name}"
        return f"Profile ({self.profile.id}, {self.profile.name}), @ {self.active_from}: {self.name}"

    def __str__(self):
        return repr(self)


db.bind(provider="sqlite", filename="tmp.sqlite3", create_db=True)
db.generate_mapping(create_tables=True)
