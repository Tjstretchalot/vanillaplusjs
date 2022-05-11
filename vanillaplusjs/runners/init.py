import decimal
from typing import Optional, Sequence
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
    argparser.add_argument(
        "--host",
        type=str,
        required=False,
        help=(
            "The host address where the website will be accessed, "
            "for e.g., updating canonical links"
        ),
    )
    args = argparser.parse_args(args)

    init(args.folder, host=args.host)


def init(folder: str, host: Optional[str] = None) -> None:
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
        host (str, None): If the host where the website will be hosted
            is known, that host to initialize the configuration with
    """
    if not os.path.exists(os.path.join(folder, "vanillaplusjs.json")):
        with open(os.path.join(folder, "vanillaplusjs.json"), "w") as f:
            json.dump(
                {
                    "version": vanillaplusjs.constants.CONFIGURATION_VERSION,
                    "host": host,
                    "images": {
                        "formats": {
                            "jpeg": {
                                "exports": {
                                    "50": {
                                        "min_area_px2": 600 * 600,
                                        "max_area_px2": None,
                                        "preference": 1,
                                        "formatter_kwargs": {"quality": 50},
                                    },
                                    "75": {
                                        "min_area_px2": None,
                                        "max_area_px2": None,
                                        "preference": 2,
                                        "formatter_kwargs": {"quality": 75},
                                    },
                                    "85": {
                                        "min_area_px2": None,
                                        "max_area_px2": None,
                                        "preference": 3,
                                        "formatter_kwargs": {"quality": 85},
                                    },
                                    "100": {
                                        "min_area_px2": None,
                                        "max_area_px2": 600 * 600,
                                        "preference": 5,
                                        "formatter_kwargs": {"quality": 100},
                                    },
                                },
                                "minimum_unit_size_bytes": 85_000,
                            },
                            "webp": {
                                "exports": {
                                    "50": {
                                        "min_area_px2": 400 * 400,
                                        "max_area_px2": None,
                                        "preference": 1,
                                        "formatter_kwargs": {
                                            "quality": 50,
                                            "method": 6,
                                            "lossless": False,
                                        },
                                    },
                                    "75": {
                                        "min_area_px2": 600 * 600,
                                        "max_area_px2": None,
                                        "preference": 2,
                                        "formatter_kwargs": {
                                            "quality": 75,
                                            "method": 6,
                                            "lossless": False,
                                        },
                                    },
                                    "85": {
                                        "min_area_px2": None,
                                        "max_area_px2": None,
                                        "preference": 3,
                                        "formatter_kwargs": {
                                            "quality": 85,
                                            "method": 6,
                                            "lossless": False,
                                        },
                                    },
                                    "100": {
                                        "min_area_px2": None,
                                        "max_area_px2": 600 * 600,
                                        "preference": 5,
                                        "formatter_kwargs": {
                                            "quality": 100,
                                            "method": 6,
                                            "lossless": False,
                                        },
                                    },
                                    "lossless": {
                                        "min_area_px2": None,
                                        "max_area_px2": 400 * 400,
                                        "preference": 8,
                                        "formatter_kwargs": {
                                            "quality": 100,
                                            "method": 6,
                                            "lossless": True,
                                        },
                                    },
                                },
                                "minimum_unit_size_bytes": 85_000,
                            },
                        },
                        "default_format": "jpeg",
                        "maximum_resolution": 7,
                        "resolution_step": decimal.Decimal(0.5),
                    },
                },
                f,
                cls=DecimalEncoder,
            )

    os.makedirs(os.path.join(folder, "src", "public", "img"), exist_ok=True)
    os.makedirs(os.path.join(folder, "src", "public", "js"), exist_ok=True)
    os.makedirs(os.path.join(folder, "src", "public", "partials"), exist_ok=True)

    if not os.path.exists(os.path.join(folder, "src", "public", "index.html")):
        with open(os.path.join(folder, "src", "public", "index.html"), "w") as f:
            print("<!DOCTYPE html>", file=f)
            print('<html lang="en">', file=f)
            print("<head>", file=f)
            print("  <title>VanillaPlusJS</title>", file=f)
            print('  <meta charset="utf-8">', file=f)
            print("</head>", file=f)
            print("<body>", file=f)
            print("  <h1>VanillaPlusJS</h1>", file=f)
            print("</body>", file=f)
            print("</html>", file=f)


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super().default(o)
