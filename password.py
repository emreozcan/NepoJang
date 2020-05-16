from passlib.context import CryptContext

password_crypto_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256",
    pbkdf2_sha256__default_rounds=30000,
)


def password_hash(cleartext):
    return password_crypto_context.hash(cleartext)


def password_compare(cleartext, hashed):
    return password_crypto_context.verify(cleartext, hashed)
