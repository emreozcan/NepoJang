import importlib
import pathlib
import argparse

modules = pathlib.Path(__file__).parent.absolute().joinpath("additional").glob("*.py")
names = [module.name for module in modules]

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("script")

args = parser.parse_known_args()

if f"{args[0].script}.py" not in names:
    print("No script exists with that name!")
    exit(1)

module = importlib.import_module(f"additional.{args[0].script}")
module.call(args[0].script, args[1])
