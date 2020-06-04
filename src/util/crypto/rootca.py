from datetime import datetime

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from paths import ROOT_PRIVATE_KEY_PATH, ROOT_PUBLIC_KEY_PATH, ROOT_CERTIFICATE_PATH


def create_and_write_root_certificate(overwrite=False):
    if not overwrite \
            and ROOT_CERTIFICATE_PATH.exists() \
            and ROOT_PRIVATE_KEY_PATH.exists() \
            and ROOT_PUBLIC_KEY_PATH.exists():
        return

    root_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend()
    )

    root_pub = root_key.public_key()

    with open(ROOT_PRIVATE_KEY_PATH, "wb") as root_key_file:
        root_key_file.write(root_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    with open(ROOT_PUBLIC_KEY_PATH, "wb") as root_pub_file:
        root_pub_file.write(root_pub.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.PKCS1
        ))

    issuer = subject = x509.Name([
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "NepoJang"),
        x509.NameAttribute(NameOID.COMMON_NAME, "(Self Trusted) NepoJang Root CA"),
    ])

    usage = x509.KeyUsage(
        digital_signature=False,
        content_commitment=False,
        key_encipherment=False,
        data_encipherment=False,
        key_agreement=False,
        key_cert_sign=True,
        crl_sign=False,
        encipher_only=False,
        decipher_only=False,
    )

    basic_constraints = x509.BasicConstraints(
        ca=True,
        path_length=0,
    )

    certificate = x509.CertificateBuilder()\
        .subject_name(subject)\
        .issuer_name(issuer)\
        .public_key(root_pub)\
        .serial_number(x509.random_serial_number())\
        .not_valid_before(datetime.utcnow())\
        .not_valid_after(datetime.max)\
        .add_extension(extension=usage, critical=True)\
        .add_extension(extension=basic_constraints, critical=True)\
        .sign(root_key, hashes.SHA512(), backend=default_backend())

    with open(ROOT_CERTIFICATE_PATH, "wb") as root_crt_file:
        root_crt_file.write(certificate.public_bytes(serialization.Encoding.PEM))


if __name__ == '__main__':
    create_and_write_root_certificate(overwrite=True)
