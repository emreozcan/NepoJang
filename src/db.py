from datetime import datetime, timedelta
from uuid import UUID, uuid4

from jwt import decode as jwt_decode, exceptions as jwt_exceptions
from pony.orm import set_sql_debug, Database, PrimaryKey, Required, Set, Optional, desc

from util.exceptions import InvalidAuthHeaderException, AuthorizationException, ExistsException
from constant.security_questions import SECURITY_QUESTIONS
from paths import DB_PATH, SKINS_ROOT, CAPES_ROOT

set_sql_debug(False)
db = Database()


class Account(db.Entity):
    id = PrimaryKey(int, auto=True)
    uuid = Required(UUID, unique=True, default=uuid4)
    username = Required(str, unique=True)  # login information, or email
    password = Required(str)  # hashed password

    profiles = Set('Profile')  # official Mojang api supports 1 profile but multiple may be supported in the future

    client_tokens = Set('ClientToken')
    trusted_ips = Set('TrustedIP')
    security_questions = Set('SecurityQuestion')

    def add_answer(self, question_id: int, answer: str):
        """Add security question

        :return: Newly created SecurityQuestion
        :raise ValueError: If a question with an invalid ID was given.
        :raise ExistsError: If the account already has a question with given ID.
        :rtype: SecurityQuestion
        """
        if question_id not in SECURITY_QUESTIONS:
            raise ValueError(f"Invalid question ID {question_id}")
        if SecurityQuestion.select(lambda x: x.account == self and x.question_id == question_id).count() != 0:
            raise ExistsException(f"This account already has a question with ID {question_id}.")
        return SecurityQuestion(
            account=self,
            question_id=question_id,
            answer=answer
        )

    def check_answers(self, answers) -> bool:
        """Check security answers

        If an incorrect answer is found, the rest of the questions aren't checked.

        :param list answers: List of {"id": int, "answer": string}
        :raise AuthorizationException:
            If incorrect amount of answers was given.
            If an answer with an invalid question ID was given.
        :raise KeyError: If an answer has incorrect structure.
        :return: Whether the answers were true or not
        """
        given_answer_count = len(answers)
        expected_answer_count = self.security_questions.count()
        if given_answer_count != expected_answer_count:
            raise AuthorizationException(f"Expected {expected_answer_count} answers, {given_answer_count} given.")

        for answer in answers:
            question_object = SecurityQuestion.get(id=answer["id"])
            if question_object is None:
                raise AuthorizationException(f"There isn't a question object with id {answer['id']}.")
            if question_object.answer != answer["answer"]:
                # raise AuthorizationException(f"Incorrect answer \"{answer['answer']}\" for {answer['id']}."
                #                              f"Correct answer is \"{question_object.answer}\".")
                # The above exception was disabled because it might accidentally be echoed back to the user.
                return False
        return True

    def does_trust_ip(self, address: str) -> bool:
        """Check if an IP is trusted

        Returns True if there are no security questions.

        :param str address: IP address to check
        :return: True if trusted, False if untrusted.
        """
        trusted_ip_object = TrustedIP.select(lambda x: x.account == self and x.address == address)
        if trusted_ip_object.count() < 1:
            return False
        return True

    def trust_ip(self, address: str):
        """Add a new trusted IP to this account.

        If the IP is already trusted, does not do anything and returns None.
        (Does not refresh the trusted IP's expiration.)

        :param str address: IP address to trust
        :return: Newly created TrustedIP object
        :rtype: TrustedIP or None
        """
        if not self.does_trust_ip(address):
            return TrustedIP(
                account=self,
                address=address
            )

    def __repr__(self):
        return f"{self.id}, {self.username}, {self.uuid}"

    def __str__(self):
        return repr(self)


class SecurityQuestion(db.Entity):
    id = PrimaryKey(int, auto=True)
    account = Required(Account)

    question_id = Required(int)
    answer = Required(str)

    def __repr__(self):
        return f"{self.id}, {SECURITY_QUESTIONS[self.question_id]} ({self.answer}) " \
               f"-of> {self.account.id}, {self.account.username}"

    def __str__(self):
        return repr(self)


class TrustedIP(db.Entity):
    id = PrimaryKey(int, auto=True)
    account = Required(Account)
    address = Required(str)

    created_utc = Required(datetime, default=datetime.utcnow)
    expiry_utc = Required(datetime, default=lambda: datetime.utcnow()+timedelta(days=14))


class Profile(db.Entity):
    id = PrimaryKey(int, auto=True)
    uuid = Required(UUID, unique=True, default=uuid4)
    account = Required(Account)
    agent = Required(str)

    access_tokens = Set('AccessToken')
    profile_name_events = Set('ProfileNameEvent')

    name = Required(str)
    name_upper = Required(str)
    name_lower = Required(str)

    profile_skin = Optional('ProfileSkin', cascade_delete=True)
    profile_cape = Optional('ProfileCape', cascade_delete=True)

    mcserver_sessions = Set('MCServerSession')

    def reset_skin(self):
        """Delete ProfileSkin and corresponding file.

        Does not raise FileNotFoundError if file was not found.
        Safe to call whether or not there's a ProfileSkin attached.
        """
        if self.profile_skin is not None:
            self.profile_skin.delete()

    def update_skin(self, image, model):
        """Create or update skin and corresponding file.

        :param PIL.Image.Image image: 64x32 or 64x64 PNG Image
        :param str model: "" for Classic, "slim" for Slim
        :raise ValueError: If image isn't PNG or the right size.
        :return: Newly created ProfileSkin
        :rtype: ProfileSkin
        """
        if image.format != "PNG":
            raise ValueError(f"Image must be in PNG format. It is {image.format}")

        width, height = image.size
        if width != 64 or height not in [32, 64]:
            raise ValueError(f"Image size must be either (64, 32) or (64, 64). It is {image.size}")

        self.reset_skin()

        profile_skin = ProfileSkin(profile=self, model=model)
        image.save(SKINS_ROOT.joinpath(profile_skin.name), format="PNG")
        return profile_skin

    def reset_cape(self):
        """Delete ProfileCape and corresponding file.

        Does not raise FileNotFoundError if file was not found.
        Safe to call whether or not there's a ProfileCape attached.
        """
        if self.profile_cape is not None:
            self.profile_cape.delete()

    def update_cape(self, image):
        """Create or update cape and corresponding file.

        :param PIL.Image.Image image: 64x32 PNG Image
        :raise ValueError: If image isn't PNG or 64x32
        :return: Newly created ProfileCape
        :rtype: ProfileCape
        """
        if image.format != "PNG":
            raise ValueError(f"Image must be in PNG format. It is {image.format}")

        width, height = image.size
        if width != 64 or height != 32:
            raise ValueError(f"Image size must be (64, 32). It is {image.size}")

        self.reset_cape()

        profile_cape = ProfileCape(profile=self)
        image.save(CAPES_ROOT.joinpath(profile_cape.name), format="PNG")
        return profile_cape

    def get_texture_data(self, textures_host) -> dict:
        """Get texture data

        The keys used will be in the format the clients are expecting.

        :return: B64 encoding ready dict
        """
        data = {
            "timestamp": int(datetime.utcnow().timestamp()*1000),
            "profileId": self.uuid.hex,
            "profileName": self.name,
            # "signatureRequired": False,  # todo?
            "textures": {

            }
        }
        if self.profile_skin is not None:
            data["textures"]["SKIN"] = {
                "url": f"http://{textures_host}/texture/{self.profile_skin.name}"
            }
            if self.profile_skin.model == "slim":
                # WHO CAME UP WITH THIS FORMAT? WHAT IS THIS???
                data["textures"]["SKIN"]["metadata"] = {"model": "slim"}
        if self.profile_cape is not None:
            data["textures"]["CAPE"] = {
                "url": f"http://{textures_host}/texture/{self.profile_cape.name}"
            }

        return data

    def force_set_name(self, new_name):
        """Set profile name without modifying history.

        Modify Profile.name, and the other styles.
        This function does not add ProfileNameEvents.
        Use Profile.attempt_name_change() for that.

        :param str new_name: New profile name
        """
        self.name = new_name
        self.name_upper = new_name.upper()
        self.name_lower = new_name.lower()

    def change_name(self, new_name_attempt):
        """Try to change profile's name.

        Change profile's name to the new name and add ProfileNameEvents.
        This function does not check name availability or whether the profile is allowed to change name.
        Use Profile.name_change_is_allowed() and Profile.name_available_for_change() for that.

        :param str new_name_attempt: New profile name
        :raise pony.orm.dbapiprovider.IntegrityError: While committing to the database if the profile name was taken.
        """
        self.force_set_name(new_name_attempt)
        ProfileNameEvent(
            profile=self,
            name=new_name_attempt
        )

    def owned_name_at(self, datetime_object: datetime):
        """Find active ProfileNameEvent at time.

        Find most recent ProfileNameEvent older than given time.

        If datetime_object is timestamp 0, returns the initial event for the profile.
        This is for compatibility. Please use Profile.get_first_name_event() for this purpose.

        :param datetime_object: Time to look up the name
        :return: ProfileNameEvent that was active at given time
        :rtype: ProfileNameEvent
        """
        if datetime == datetime.utcfromtimestamp(0):
            self.initial_name_event()

        pne = ProfileNameEvent.select(lambda x: x.profile == self and x.active_from < datetime_object)\
            .order_by(desc(ProfileNameEvent.active_from))
        return pne.first()

    @staticmethod
    def that_owned_name_at(name, datetime_object: datetime):
        """Find profile that owned the name at time.

        :param name: Case-insensitive profile name
        :param datetime_object: Time to look up the UUID
        :return: ProfileNameEvent that defined the owner of the name at given time
        :rtype: ProfileNameEvent or None
        """
        event = ProfileNameEvent.select(lambda x: (x.name == name
                                        or x.name_upper == name.upper()
                                        or x.name_lower == name.lower())
                                        and x.active_from < datetime_object)\
            .order_by(desc(ProfileNameEvent.active_from)).first()

        if event is None:
            return None

        if ProfileNameEvent.select(lambda x: x.profile == event.profile
                                   and x.active_from > event.active_from
                                   and x.active_from < datetime_object).exists():
            return None

        return event

    def initial_name_event(self):
        """Get initial NameEvent for this profile.

        :rtype: ProfileNameEvent
        """
        return ProfileNameEvent.select(lambda x: x.profile == self).order_by(ProfileNameEvent.active_from).first()

    def active_name_event(self):
        """Get active NameEvent for this profile.

        :rtype: ProfileNameEvent
        """
        return ProfileNameEvent.select(lambda x: x.profile == self).order_by(desc(ProfileNameEvent.active_from)).first()

    def time_of_next_name_change(self) -> datetime:
        """Find when profile name can be changed.

        :return: Datetime when profile name can be changed
        """
        return self.active_name_event().active_from + timedelta(days=30)

    def time_to_name_change(self) -> timedelta:
        """Find when profile name can be changed.

        :return: Timedelta which needs to be waited before profile name can be changed
        """
        return self.time_of_next_name_change() - datetime.utcnow()

    def can_change_name(self) -> bool:
        """Find if profile name can be changed.

        :return: True if 30 days has passed after last Profile name change
        """
        return self.time_to_name_change() < timedelta(0)

    @staticmethod
    def time_of_name_release(name) -> datetime:
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
    def time_to_name_release(name) -> timedelta:
        """Find when profile name will be released.

        This function assumes that the name is taken and the previous owner doesn't change it back.

        Returns negative timedelta if name was released in the past.

        :param name: Case-insensitive profile name
        :return: Timedelta which needs to be waited before profile name can be changed
        """
        return Profile.time_of_name_release(name) - datetime.utcnow()

    def is_name_available_for_change(self, name) -> bool:
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
        return Profile.is_name_available_for_creation(name)

    @staticmethod
    def is_name_available_for_creation(name) -> bool:
        """Determine if this name is released.

        Released means it has passed 37 days after the name was last used by another profile.
        Name can be used to create a new profile if this returns True.

        :param name: Case-insensitive profile name
        :return: True if name is released
        """
        return Profile.time_to_name_release(name) < timedelta(0)

    @staticmethod
    def create(*args, **kwargs):
        """Create a new profile.

        Creates and returns a new profile instance.
        Also creates a ProfileNameEvent.

        This function does not check if name is available.
        Use Profile.name_available_for_creation() for that.

        :param args: Arguments will be passed onto Profile.
        :param kwargs: Keyword arguments will be passed onto Profile. "name" is required for this function.
        :raise ExistsError: If name was already taken
        :return: Newly created profile object
        :rtype: Profile
        """

        if not Profile.is_name_available_for_creation(kwargs["name"]):
            raise ExistsException("A profile with this name already exists!")

        new_profile = Profile(*args, **kwargs)
        ProfileNameEvent(
            active_from=datetime.utcfromtimestamp(0),
            profile=new_profile,
            name=kwargs["name"]
        )
        return new_profile

    @staticmethod
    def get_profile_with_name(name):
        """Get profile with case-insensitive name

        :param name: Case-insensitive name
        :rtype: Profile or None
        """
        return Profile.get(lambda x: x.name == name
                           or x.name_upper == name.upper()
                           or x.name_lower == name.lower())

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


class MCServerSession(db.Entity):
    id = PrimaryKey(int, auto=True)

    profile = Required(Profile)
    client_side_ip = Required(str)
    server_hash = Required(str)

    created_utc = Required(datetime, default=datetime.utcnow)


class ClientToken(db.Entity):
    id = PrimaryKey(int, auto=True)
    uuid = Required(UUID, unique=True, default=uuid4)
    account = Required(Account)  # which account does this client token authorize
    access_tokens = Set('AccessToken')

    created_utc = Required(datetime, default=datetime.utcnow)
    expiry_utc = Required(datetime, default=lambda: datetime.utcnow()+timedelta(days=30))

    def refresh(self, days=30) -> datetime:
        """Add days to expiry_utc

        New expiry date will be "now+days"

        :param int days: Amount of days to add to today
        :return: Naive UTC datetime of "days" days later.
        """
        self.expiry_utc = datetime.utcnow()+timedelta(days=days)
        return self.expiry_utc

    def __repr__(self):
        return f"{self.id}, {self.uuid}, related {self.access_tokens.count()} AccessTokens " \
               f"-of> {self.account.id}, {self.account.username}"

    def __str__(self):
        return repr(self)


class AccessToken(db.Entity):
    id = PrimaryKey(int, auto=True)
    uuid = Required(UUID, unique=True, default=uuid4)
    issuer = Required(str, default="Yggdrasil-Auth")
    client_token = Required(ClientToken)  # client that created this access token

    authentication_valid = Required(bool, default=True)  # is access token valid for authenticating with game servers
    profile = Optional(Profile)  # which profile can this access token grants access to

    created_utc = Required(datetime, default=datetime.utcnow)
    expiry_utc = Required(datetime, default=lambda: datetime.utcnow()+timedelta(days=2))

    @staticmethod
    def from_header(header):
        """Get AccessToken from Authorization Header

        :param str header: HTTP Request Header 'Authorization': 'Bearer <token>'
        :raise InvalidAuthHeaderException: If Header doesn't start with "Bearer " or is empty.
        :rtype: AccessToken or None
        """
        if header is None or not header.startswith("Bearer ") or header == "Bearer ":
            raise InvalidAuthHeaderException()

        return AccessToken.from_token(header[7:])

    def refresh(self, days=2) -> datetime:
        """Add days to expiry_utc

        New expiry date will be "now+days"

        :param int days: Amount of days to add to today
        :return: Naive UTC datetime of "days" days later.
        """
        self.expiry_utc = datetime.utcnow()+timedelta(days=days)
        return self.expiry_utc

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

    @staticmethod
    def from_token(token):
        """Get AccessToken from token string

        :param UUID or str token: JWT encoded token or token UUID string, either dashed or not, or UUID object
        :rtype: AccessToken or None
        """
        if isinstance(token, str):
            try:
                uuid_object = UUID(token)
            except ValueError:  # token is invalid UUID, may be JWT
                try:
                    jwt_decoded = jwt_decode(jwt=token, verify=False)
                    uuid_object = UUID(jwt_decoded["yggt"])
                except (jwt_exceptions.DecodeError, jwt_exceptions.InvalidAlgorithmError, ValueError):
                    return None
                else:
                    return AccessToken.get(uuid=uuid_object)
            else:  # token is valid UUID
                return AccessToken.get(uuid=uuid_object)

        elif isinstance(token, UUID):
            return AccessToken.get(uuid=token)

        return None

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

    def repr_timestamp(self):
        """Use integer timestamps instead of human readable time like in __repr__()"""
        return f"Profile ({self.profile.id}, {self.profile.name}), " \
               f"{'created with' if self.is_initial_name else 'changed name'} " \
               f"@ {self.active_from.timestamp()}: {self.name}"

    def __repr__(self):
        return f"Profile ({self.profile.id}, {self.profile.name}), " \
               f"{'created with' if self.is_initial_name else 'changed name'} " \
               f"@ {self.active_from}: {self.name}"

    def __str__(self):
        return repr(self)


class ProfileSkin(db.Entity):
    id = PrimaryKey(int, auto=True)
    profile = Required(Profile)

    name = Required(str, unique=True, default=lambda: "".join([uuid4().hex, uuid4().hex]))
    model = Optional(str)  # "" or None if Steve, "slim" if Alex.

    def before_delete(self):
        SKINS_ROOT.joinpath(self.name).unlink()


class ProfileCape(db.Entity):
    id = PrimaryKey(int, auto=True)
    profile = Required(Profile)

    name = Required(str, unique=True, default=lambda: "".join([uuid4().hex, uuid4().hex]))

    def before_delete(self):
        CAPES_ROOT.joinpath(self.name).unlink()


db.bind(provider="sqlite", filename=str(DB_PATH), create_db=True)
db.generate_mapping(create_tables=True)
