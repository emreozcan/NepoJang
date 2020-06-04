from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from paths import JWT_PRIVATE_KEY_PATH, JWT_PUBLIC_KEY_PATH, JWT_PUBLIC_KEY_DER_PATH


def create_and_write_jwt_keys(overwrite=False):
    if not overwrite \
            and JWT_PUBLIC_KEY_DER_PATH.exists() \
            and JWT_PUBLIC_KEY_PATH.exists() \
            and JWT_PRIVATE_KEY_PATH.exists():
        return

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend()
    )

    public_key = private_key.public_key()

    with open(JWT_PRIVATE_KEY_PATH, "wb") as jwt_key_file:
        jwt_key_file.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    with open(JWT_PUBLIC_KEY_PATH, "wb") as jwt_pub_file:
        jwt_pub_file.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.PKCS1
        ))

    with open(JWT_PUBLIC_KEY_DER_PATH, "wb") as jwt_der_file:
        jwt_der_file.write(public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.PKCS1
        ))


if __name__ == '__main__':
    create_and_write_jwt_keys(overwrite=True)

JWT_PRIVATE_KEY_BYTES = JWT_PRIVATE_KEY_PATH.read_bytes()
JWT_PUBLIC_KEY_BYTES = JWT_PUBLIC_KEY_PATH.read_bytes()
