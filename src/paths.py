import pathlib

SRC = pathlib.Path(__file__).parent
PROJECT_ROOT = SRC.parent
DATA_ROOT = PROJECT_ROOT.joinpath("data")

DB_PATH = DATA_ROOT.joinpath("tmp.sqlite3")

TEXTURES_ROOT = DATA_ROOT.joinpath("textures")
SKINS_ROOT = TEXTURES_ROOT.joinpath("skins")

ROOTS = [PROJECT_ROOT, DATA_ROOT, TEXTURES_ROOT, SKINS_ROOT]


def setup():
    for root in ROOTS:
        try:
            root.mkdir()
        except FileExistsError:
            pass


if __name__ == '__main__':
    setup()
