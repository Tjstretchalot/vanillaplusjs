from typing import Sequence
import argparse


def main(args: Sequence[str]):
    argparser = argparse.ArgumentParser(
        prog="vanillajsplus dev",
        description=(
            "Builds the webserver in development mode and "
            "runs the webserver on the given port"
        ),
    )
    argparser.add_argument("port", type=int, help="The port to run the webserver on")
    argparser.add_argument(
        "--watch", action="store_true", help="Watch for changes and rebuild"
    )
    args = argparser.parse_args(args)
