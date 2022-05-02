from typing import Sequence
import argparse


def main(args: Sequence[str]):
    argparser = argparse.ArgumentParser(
        prog="vanillajsplus build",
        description="Builds the static files, storing them in out/www",
    )
    argparser.add_argument(
        "--dev", action="store_true", help="Build for development specifically"
    )
    argparser.add_argument(
        "--infolder",
        type=str,
        default=".",
        help=(
            "The base folder to search from. Should contain "
            "src/public and vanillaplus.json"
        ),
    )
    argparser.add_argument(
        "--outfolder",
        type=str,
        default="out",
        help=(
            "Where to store the built files. Also used for storing some temporary "
            "build artifacts"
        ),
    )
    args = argparser.parse_args(args)
