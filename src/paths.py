import pathlib

SRC = pathlib.Path(__file__).parent
PROJECT_ROOT = SRC.parent
DATA_ROOT = PROJECT_ROOT.joinpath("data")

try:
    DATA_ROOT.mkdir()
except FileExistsError:
    pass

DB_PATH = DATA_ROOT.joinpath("tmp.sqlite3")

TEXTURES_ROOT = DATA_ROOT.joinpath("textures")

try:
    TEXTURES_ROOT.mkdir()
except FileExistsError:
    pass

SKINS_ROOT = TEXTURES_ROOT.joinpath("skins")

try:
    SKINS_ROOT.mkdir()
except FileExistsError:
    pass