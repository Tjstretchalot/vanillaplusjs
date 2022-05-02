from typing import Sequence
import argparse
import os
import vanillaplusjs.constants
import json


def main(args: Sequence[str]) -> None:
    argparser = argparse.ArgumentParser(
        prog="vanillajsplus init", description="Initializes the folder structure"
    )
    argparser.add_argument(
        "--folder",
        type=str,
        default=".",
        help="The folder to initialize",
    )
    args = argparser.parse_args(args)

    init(args.folder)


def init(folder: str) -> None:
    """Initializes the given folder with vanillaplusjs. If the configuration
    file does not exist it is initializes, and if the folder structure does not
    exist it is initializes.

    After this function completes, the folder structure is as follows:

    ```
    src/
        public/
            img/
            js/
            partials/
    vanillaplusjs.json
    ```

    Args:
        folder (str): The root folder to initialize
    """
    if not os.path.exists(os.path.join(folder, "vanillaplusjs.json")):
        with open(os.path.join(folder, "vanillaplusjs.json"), "w") as f:
            json.dump(
                {
                    "version": vanillaplusjs.constants.CONFIGURATION_VERSION,
                },
                f,
            )

    os.makedirs(os.path.join(folder, "src", "public", "img"), exist_ok=True)
    os.makedirs(os.path.join(folder, "src", "public", "js"), exist_ok=True)
    os.makedirs(os.path.join(folder, "src", "public", "partials"), exist_ok=True)
