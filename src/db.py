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
        """Set profile name without modifying history.

        Modify Profile.name, and the other styles.
        This function does not add ProfileNameEvents.
        Use Profile.attempt_name_change() for that.

        :param str new_name: New profile name
        """
        self.name = new_name
        self.name_upper = new_name.upper()
        self.name_lower = new_name.lower()

    def attempt_name_change(self, new_name_attempt):
        """Try to change profile's name.

        Change profile's name to the new name and add ProfileNameEvents.
        This function does not check name availability or whether the profile is allowed to change name.
        Use Profile.name_change_is_allowed() and Profile.name_available_for_change() for that.

        :param str new_name_attempt: New profile name
        :raise pony.orm.dbapiprovider.IntegityError: While commiting to the database if the profile name was taken
        """
        self.set_name_and_styles(new_name_attempt)
        ProfileNameEvent(
            profile=self,
            name=new_name_attempt
        )

    def get_name_event_at(self, datetime_object: datetime):
        """Find active ProfileNameEvent at time.

        Find most recent ProfileNameEvent older than given time.

        If datetime_object is timestamp 0, returns the initial event for the profile.
        This is for compatibility. Please use Profile.get_first_name_event() for this purpose.

        :param datetime_object: Time to look up the name
        :return: ProfileNameEvent that was active at given time
        :rtype: ProfileNameEvent
        """

        if datetime == datetime.utcfromtimestamp(0):
            self.get_first_name_event()

        pne = ProfileNameEvent.select(lambda x: x.profile == self and x.active_from < datetime_object)\
            .order_by(desc(ProfileNameEvent.active_from))
        return pne.first()

    def get_first_name_event(self):
        """Get initial NameEvent for this profile.

        :rtype: ProfileNameEvent
        """
        return ProfileNameEvent.select(lambda x: x.profile == self).order_by(ProfileNameEvent.active_from).first()

    def get_last_name_event(self):
        """Get active NameEvent for this profile.

        :rtype: ProfileNameEvent
        """
        return ProfileNameEvent.select(lambda x: x.profile == self).order_by(desc(ProfileNameEvent.active_from)).first()

    def name_change_time_until(self) -> datetime:
        """Find when profile name can be changed.

        :return: Datetime when profile name can be changed
        """
        return self.get_last_name_event().active_from + timedelta(days=30)

    def name_change_wait_delta(self) -> timedelta:
        """Find when profile name can be changed.

        :return: Timedelta which needs to be waited before profile name can be changed
        """
        return self.name_change_time_until() - datetime.utcnow()

    def name_change_is_allowed(self) -> bool:
        """Find if profile name can be changed.

        :return: True if 30 days has passed after last Profile name change
        """
        return self.name_change_wait_delta() < timedelta(0)

    @staticmethod
    def name_taken_time_until(name) -> datetime:
        """Find when profile name will be released.

        This function assumes that the name is taken and the previous owner doesn't change it back.

        Returns timestamp 0 if profile name was never used before.

        :param name: Case-insensitive profile name
        :return: Datetime when profile name gets released
        """
        event = ProfileNameEvent.last_event(name)
        if event is None:
            return datetime.utcfromtimestamp(0)
        return event.active_from + timedelta(days=37)

    @staticmethod
    def name_taken_wait_delta(name) -> timedelta:
        """Find when profile name will be released.

        This function assumes that the name is taken and the previous owner doesn't change it back.

        Returns negative timedelta if name was released in the past.

        :param name: Case-insensitive profile name
        :return: Timedelta which needs to be waited before profile name can be changed
        """
        return Profile.name_taken_time_until(name) - datetime.utcnow()

    def name_available_for_change(self, name) -> bool:
        """Determine if this name is available.

        This function does not check whether profile is allowed to change names.
        Use Profile.name_change_is_allowed() for that.

        :param name: Case-insensitive profile name
        :return: True if name is available right now
        """
        event = ProfileNameEvent.last_event(name)
        if event is None:  # This name was never used before.
            return True
        if event.profile == self:
            return True
        return Profile.name_available_for_creation(name)

    @staticmethod
    def name_available_for_creation(name) -> bool:
        """Determine if this name is released.

        Released means it has passed 37 days after the name was last used by another profile.
        Name can be used to create a new profile if this returns True.

        :param name: Case-insensitive profile name
        :return: True if name is released
        """
        return Profile.name_taken_wait_delta(name) < timedelta(0)

    @staticmethod
    def create_profile_and_history(*args, **kwargs):
        """Create a new profile.

        Creates and returns a new profile instance.
        Also creates a ProfileNameEvent.

        This function does not check if name is available.
        Use Profile.name_available_for_creation() for that.

        :param args: Arguments will be passed onto Profile.
        :param kwargs: Keyword arguments will be passed onto Profile. "name" is required for this function.
        :return: Newly created profile object
        :rtype: Profile
        """
        new_profile = Profile(*args, **kwargs)
        ProfileNameEvent(
            profile=new_profile,
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

    def __repr__(self):
        return f"{self.id}, {self.uuid}, related {self.access_tokens.count()} AccessTokens " \
               f"-of> {self.account.id}, {self.account.username}"

    def __str__(self):
        return repr(self)


class AccessToken(db.Entity):
    id = PrimaryKey(int, auto=True)
    uuid = Required(UUID, unique=True, default=uuid4)
    issuer = Required(str, default="Yggdrasil-Auth")
    created_utc = Required(datetime, default=datetime.utcnow)
    expiry_utc = Required(datetime, default=lambda: datetime.utcnow()+timedelta(days=2))
    authentication_valid = Required(bool, default=True)  # is access token valid for authenticating with game servers
    client_token = Required(ClientToken)  # client that created this access token
    profile = Optional(Profile)  # which profile can this access token grants access to

    def format(self) -> dict:
        """Format self to respond to the client.

        The keys used will be in the format the clients are expecting.

        :return: dict ready for JWT encoding
        """
        data = {  # There are really bad key names, but this is how the API is.
            "sub": self.client_token.account.uuid.hex,
            "yggt": self.uuid.hex,
            "issr": self.issuer,
            "exp": int(self.expiry_utc.timestamp()),
            "iat": int(self.created_utc.timestamp())
        }
        if self.profile:
            data["spr"] = self.profile.uuid.hex
        return data

    def __repr__(self):
        return f"{self.id}, {self.uuid}, {'valid' if self.authentication_valid else 'invalid'}, " \
               f"{self.created_utc} to {self.expiry_utc}, by {self.issuer}, {self.client_token.id}, " \
               f"{'generic' if self.profile is None else f'for {self.profile.id}, {self.profile.name}'} " \
               f"-of> {self.client_token.account.id}, {self.client_token.account.username}"

    def __str__(self):
        return repr(self)


class ProfileNameEvent(db.Entity):
    id = PrimaryKey(int, auto=True)
    profile = Required(Profile)
    active_from = Required(datetime, default=datetime.utcnow)
    name = Required(str)
    name_upper = Required(str)
    name_lower = Required(str)

    @property
    def is_initial_name(self) -> bool:
        """Determine if this is the first name of a profile."""
        return not ProfileNameEvent.select(lambda x: x.profile == self.profile and x.active_from < self.active_from)\
            .exists()

    @staticmethod
    def last_event(name):
        """Return the most recent event with this name.

        :param name: Case-insensitive profile name
        :rtype: ProfileNameEvent
        :return: Active ProfileNameEvent with this name
        """
        return ProfileNameEvent.select(lambda x: x.name == name
                                       or x.name_upper == name.upper()
                                       or x.name_lower == name.lower())\
            .order_by(desc(ProfileNameEvent.active_from)).first()

    def __init__(self, *args, **kwargs):
        if "name_upper" not in kwargs:
            kwargs["name_upper"] = kwargs["name"].upper()
        if "name_lower" not in kwargs:
            kwargs["name_lower"] = kwargs["name"].lower()
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"Profile ({self.profile.id}, {self.profile.name}), " \
               f"{'created with' if self.is_initial_name else 'changed name'} " \
               f"@ {self.active_from}: {self.name}"

    def __str__(self):
        return repr(self)


db.bind(provider="sqlite", filename="tmp.sqlite3", create_db=True)
db.generate_mapping(create_tables=True)
