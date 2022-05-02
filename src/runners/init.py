from typing import Sequence
import argparse


def main(args: Sequence[str]):
    argparser = argparse.ArgumentParser(
        prog="vanillajsplus init", description="Initializes the folder structure"
    )
    args = argparser.parse_args(args)
