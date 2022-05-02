from typing import Sequence
import argparse


def main(args: Sequence[str]):
    argparser = argparse.ArgumentParser(
        prog="vanillajsplus clean",
        description="Removes the generated files (out/, artifacts/)",
    )
    args = argparser.parse_args(args)
