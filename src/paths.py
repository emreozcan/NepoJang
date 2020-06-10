import pathlib

SRC = pathlib.Path(__file__).parent
PROJECT_ROOT = SRC.parent
DATA_ROOT = PROJECT_ROOT.joinpath("data")

DB_PATH = DATA_ROOT.joinpath("tmp.sqlite3")

TEXTURES_ROOT = DATA_ROOT.joinpath("textures")
SKINS_ROOT = TEXTURES_ROOT.joinpath("skins")
CAPES_ROOT = TEXTURES_ROOT.joinpath("capes")

RESOURCES_ROOT = PROJECT_ROOT.joinpath("res")

CRYPTO_ROOT = RESOURCES_ROOT.joinpath("crypto")
HTTP_PRIVATE_KEY_PATH = CRYPTO_ROOT.joinpath("http.key")
HTTP_CERTIFICATE_PATH = CRYPTO_ROOT.joinpath("http.crt")
HTTP_PUBLIC_KEY_PATH = CRYPTO_ROOT.joinpath("http.pub")
HTTP_CERT_REQUEST_PATH = CRYPTO_ROOT.joinpath("http.csr")

ROOT_PRIVATE_KEY_PATH = CRYPTO_ROOT.joinpath("root.key")
ROOT_PUBLIC_KEY_PATH = CRYPTO_ROOT.joinpath("root.pub")
ROOT_CERTIFICATE_PATH = CRYPTO_ROOT.joinpath("root.crt")

ROOTS = [
    PROJECT_ROOT,
    DATA_ROOT,
    TEXTURES_ROOT,
    SKINS_ROOT,
    CAPES_ROOT,
    RESOURCES_ROOT,
    CRYPTO_ROOT,
]


def setup():
    for root in ROOTS:
        try:
            root.mkdir()
        except FileExistsError:
            pass


if __name__ == '__main__':
    setup()
