from datetime import datetime, timedelta

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID

from paths import HTTP_PRIVATE_KEY_PATH, HTTP_PUBLIC_KEY_PATH, HTTP_CERT_REQUEST_PATH, HTTP_CERTIFICATE_PATH,\
    ROOT_CERTIFICATE_PATH, ROOT_PRIVATE_KEY_PATH


def create_and_write_http_keys(overwrite=False) -> rsa.RSAPrivateKeyWithSerialization:
    if not overwrite and HTTP_PUBLIC_KEY_PATH.exists() and HTTP_PRIVATE_KEY_PATH.exists():
        return serialization.load_pem_private_key(
            data=HTTP_PRIVATE_KEY_PATH.read_bytes(),
            password=None,
            backend=default_backend()
        )

    http_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend()
    )

    http_pub = http_key.public_key()

    with open(HTTP_PRIVATE_KEY_PATH, "wb") as http_key_file:
        http_key_file.write(http_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    with open(HTTP_PUBLIC_KEY_PATH, "wb") as http_pub_file:
        http_pub_file.write(http_pub.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.PKCS1
        ))

    return http_key


def create_and_write_csr(http_key: rsa.RSAPrivateKeyWithSerialization, domains: list, overwrite=True) \
        -> x509.CertificateSigningRequest:
    if not overwrite and HTTP_CERT_REQUEST_PATH.exists():
        return x509.load_pem_x509_csr(
            data=HTTP_CERT_REQUEST_PATH.read_bytes(),
            backend=default_backend()
        )

    subject = x509.Name([
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "NepoJang"),
        x509.NameAttribute(NameOID.COMMON_NAME, f"NepoJang HTTP API Certificate"),
    ])

    alt_names = []
    for domain in domains:
        alt_names.append(x509.DNSName(domain))

    certificate_request = x509.CertificateSigningRequestBuilder()\
        .subject_name(subject)\
        .add_extension(x509.SubjectAlternativeName(alt_names), critical=False)\
        .sign(http_key, hashes.SHA512(), default_backend())

    with open(HTTP_CERT_REQUEST_PATH, "wb") as http_csr_file:
        http_csr_file.write(certificate_request.public_bytes(serialization.Encoding.PEM))

    return certificate_request


def issue_and_write_certificate(certificate_request, overwrite=True) -> None:
    if not overwrite and HTTP_CERTIFICATE_PATH.exists():
        return

    root_key = serialization.load_pem_private_key(
        data=ROOT_PRIVATE_KEY_PATH.read_bytes(),
        backend=default_backend(),
        password=None
    )

    root_cert = x509.load_pem_x509_certificate(
        data=ROOT_CERTIFICATE_PATH.read_bytes(),
        backend=default_backend()
    )

    new_cert = x509.CertificateBuilder()\
        .subject_name(certificate_request.subject)\
        .issuer_name(root_cert.subject)\
        .public_key(certificate_request.public_key())\
        .serial_number(x509.random_serial_number())\
        .not_valid_before(datetime.utcnow())\
        .not_valid_after(datetime.utcnow()+timedelta(days=365.2425))\

    for extension in certificate_request.extensions:
        new_cert = new_cert.add_extension(extension.value, extension.critical)

    usage = x509.KeyUsage(
        digital_signature=True,
        content_commitment=False,
        key_encipherment=True,
        data_encipherment=False,
        key_agreement=False,
        key_cert_sign=False,
        crl_sign=False,
        encipher_only=False,
        decipher_only=False
    )

    basic_constraints = x509.BasicConstraints(
        ca=False,
        path_length=None
    )

    extended_usage = x509.ExtendedKeyUsage([
        ExtendedKeyUsageOID.SERVER_AUTH,
    ])

    new_cert = new_cert\
        .add_extension(extension=usage, critical=True)\
        .add_extension(extension=basic_constraints, critical=True)\
        .add_extension(extension=extended_usage, critical=True)

    new_cert = new_cert.sign(root_key, hashes.SHA512(), backend=default_backend())

    with open(HTTP_CERTIFICATE_PATH, "wb") as http_crt_file:
        http_crt_file.write(new_cert.public_bytes(serialization.Encoding.PEM))


if __name__ == '__main__':
    http_key = create_and_write_http_keys(overwrite=False)
    csr = create_and_write_csr(http_key=http_key, domains=["localhost"], overwrite=True)
    issue_and_write_certificate(csr, overwrite=True)
