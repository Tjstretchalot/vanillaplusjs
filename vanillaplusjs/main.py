import argparse
from enum import Enum
import runners.init
import runners.build
import runners.run
import runners.dev
import runners.clean
import sys


class Command(Enum):
    """The valid commands, which dictates the behavior of the program."""

    init = "init"
    """Initializes all necessary folders and files"""

    build = "build"
    """Builds the static website"""

    run = "run"
    """Launches a basic development-only webserver for hosting the website"""

    clean = "clean"
    """Removes all generated files"""

    dev = "dev"
    """Builds and then runs the webserver"""

    def __str__(self):
        return self.value


def main():
    parser = argparse.ArgumentParser(
        description="A web-frontend near-vanilla framework. Try [COMMAND] -h for more info."
    )
    parser.add_argument("command", type=Command, choices=list(Command))

    opts = parser.parse_args(sys.argv[1:2])
    subargs = sys.argv[2:]
    if opts.command == Command.init:
        runners.init.main(subargs)
    elif opts.command == Command.build:
        runners.build.main(subargs)
    elif opts.command == Command.run:
        runners.run.main(subargs)
    elif opts.command == Command.clean:
        runners.clean.main(subargs)
    elif opts.command == Command.dev:
        runners.dev.main(subargs)
    else:
        raise ValueError("Invalid command")


if __name__ == "__main__":
    main()
