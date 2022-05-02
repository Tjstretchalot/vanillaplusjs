from typing import Sequence
import argparse


def main(args: Sequence[str]):
    argparser = argparse.ArgumentParser(
        prog="vanillajsplus build",
        description="Builds the static files, storing them in out/www",
    )
    argparser.add_argument(
        '--dev', action='store_true', help='Build for development specifically'
    )
    args = argparser.parse_args(args)
