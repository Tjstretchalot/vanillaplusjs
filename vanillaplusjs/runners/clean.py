from typing import Sequence
import argparse
import os
import shutil
import sys


def main(args: Sequence[str]):
    argparser = argparse.ArgumentParser(
        prog="vanillajsplus clean",
        description="Removes the generated files (out/, artifacts/)",
    )
    argparser.add_argument(
        "--folder",
        type=str,
        default=".",
        help="The folder containing vanillaplusjs.json",
    )

    args = argparser.parse_args(args)
    clean(args.folder)


def clean(folder: str) -> None:
    """Removes the generated files in the vanillaplusjs project at the given
    folder.

    Args:
        folder (str): The folder containing vanillaplusjs.json
    """
    if not os.path.exists(os.path.join(folder, "vanillaplusjs.json")):
        print("vanillaplusjs.json not found. Call 'vanillaplusjs init' to create it.")
        sys.exit(1)

    shutil.rmtree(os.path.join(folder, "out"), ignore_errors=True)
    shutil.rmtree(os.path.join(folder, "artifacts"), ignore_errors=True)
