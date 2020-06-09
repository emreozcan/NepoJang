from passlib.context import CryptContext
import jwt

from db import Account

password_crypto_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256",
    pbkdf2_sha256__default_rounds=30000,
)


def password_hash(cleartext: str):
    return password_crypto_context.hash(cleartext)


def password_compare(cleartext: str, hashed: str):
    return password_crypto_context.verify(cleartext, hashed)


def read_yggt(access_token_string: str):
    """
    :param access_token_string: 32 or 36 char UUID or JWT
    :return: yggt value
    """
    if len(access_token_string) == 32:
        return access_token_string
    elif len(access_token_string) == 36:
        return access_token_string.replace("-", "")
    else:
        return jwt.decode(jwt=access_token_string, verify=False)["yggt"]


def attempt_login(username: str, password: str):
    """Try to log user in

    :param username: Account username
    :param password: Cleartext account password
    :return: Account if credentials correct, None otherwise.
    :rtype: Account or None
    """
    account = Account.get(lambda a: a.username == username)
    if account is None or not password_compare(password, account.password):
        return None
    return account
