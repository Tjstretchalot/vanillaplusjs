from typing import Sequence
import argparse


def main(args: Sequence[str]):
    argparser = argparse.ArgumentParser(prog="vanillajsplus run", description="")
    argparser.add_argument("port", type=int, help="The port to run the webserver on")
    args = argparser.parse_args(args)
