from dataclasses import dataclass
from typing import Literal
from vanillaplusjs.build.build_context import BuildContext
from vanillaplusjs.build.ioutil import PeekableTextIO
import io
import json
import os
from PIL import Image, UnidentifiedImageError


Image.MAX_IMAGE_PIXELS = 1_000_000_000


@dataclass
class ImageCommand:
    """Describes the arguments for injecting an image into a document."""

    path: str
    """The path to the image; if it starts with a '/', then it's referring
    to the public folder, otherwise it's relative to the file being processed
    """

    width: int
    """The desired width of the img element. This is no wider than the
    actual image
    """

    height: int
    """The desired height of the img element. This is no taller than the
    actual image
    """

    crop_style: Literal["cover"]
    """The crop style to use when changing the aspect ratio of the image
    to fit the desired dimensions.
    """

    crop_arguments: dict
    """Arguments to the crop function, based on the crop function.
    """

    lazy: bool
    """True to load the image lazily via the lazy attribute, false to
    load the image eagerly.
    """

    def source_path_relative_to_root(
        self, context: BuildContext, command_file_path: str
    ) -> str:
        """Determines where the image is located relative to the root
        of the project.
        """
        if self.path.startswith("/"):
            return os.path.join(
                "src", "public", self.path[1:].replace("/", os.path.sep)
            )

        abs_path = os.path.abspath(
            os.path.join(
                os.path.dirname(command_file_path), self.path.replace("/", os.path.sep)
            )
        )
        return os.path.relpath(abs_path, context.folder)


def parse_command(args: str) -> ImageCommand:
    """Parses the given arguments as a command string, if it is valid.

    Expects the args to be split with spaces*, and to be of the form

    ```
    source_path width height [crop_style] [crop_arguments] [lazy]
    ```

    Where crop_arguments is a json object literal, and lazy is the literal
    "lazy" for lazy loading and "eager" for eager loading.

    *The crop arguments may have spaces within the curly brackets

    Examples:
    ```
    /img/test.jpg 25 25
    /img/test.jpg 25 50 cover {"min_top_crop": 5} lazy
    ```


    Args:
        args (str): The arguments to parse.

    Returns:
        ImageCommand: The parsed command.

    Raises:
        ValueError: If the arguments are invalid.
    """
    if not args:
        raise ValueError("No arguments given")

    args = args.split(maxsplit=4)
    if len(args) < 1:
        raise ValueError("expected source path")

    source_path = args[0]

    if len(args) < 2:
        raise ValueError("expected width")

    width = args[1]
    try:
        width = int(width)
    except ValueError:
        raise ValueError(f"expected width to be an integer; got {repr(width)}")

    if len(args) < 3:
        raise ValueError("expected height")

    height = args[2]
    try:
        height = int(height)
    except ValueError:
        raise ValueError(f"expected height to be an integer; got {repr(height)}")

    crop_style = "cover"
    if len(args) > 3:
        crop_style = args[3]
        if crop_style != "cover":
            raise ValueError(f"unsupported crop style: {repr(crop_style)}")

    crop_arguments = dict()
    if len(args) > 4:
        crop_arguments_str = args[4]
        p = PeekableTextIO(io.StringIO(crop_arguments_str))
        peeked = p.peek(1)
        if peeked != "{":
            raise ValueError(
                f"expected crop arguments to be a JSON object; got {repr(crop_arguments_str)}"
            )

        real_crop_arguments = p.read(1)
        while True:
            peeked = p.peek(1)
            if not peeked:
                raise ValueError(
                    f"expected crop arguments to be a JSON object; got {repr(crop_arguments_str)}"
                )
            real_crop_arguments += p.read(1)
            if peeked == "}":
                break

        remaining_arguments = p.read()
        if remaining_arguments and remaining_arguments[0] == " ":
            args = args[:4] + [real_crop_arguments, remaining_arguments]

        try:
            crop_arguments = json.loads(real_crop_arguments)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"expected crop arguments to be a JSON object; got {repr(crop_arguments_str)}"
            )

    lazy = True
    if len(args) > 5:
        lazy = args[5] == "lazy"

    return ImageCommand(
        path=source_path,
        width=width,
        height=height,
        crop_style=crop_style,
        crop_arguments=crop_arguments,
        lazy=lazy,
    )


def validate_command(
    command: ImageCommand, context: BuildContext, command_file_path: str
) -> bool:
    path_relative_to_root = command.source_path_relative_to_root(
        context, command_file_path
    )
    if not path_relative_to_root.startswith(os.path.join("src", "public")):
        return False

    try:
        img = Image.open(os.path.join(context.folder, path_relative_to_root))
        if img.width < command.width:
            return False
        if img.height < command.height:
            return False
        img.close()
    except FileNotFoundError:
        return False
    except UnidentifiedImageError:
        return False

    return True
