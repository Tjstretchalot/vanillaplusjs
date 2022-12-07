"""This handler glues the images HTML manipulator so that the output can be
accessed via javascript.

In particular, this will act on files that are of the form `*.images.json`,
will parse the file as a list of jsonified ImageCommands. This will handle
exporting those image commands - which involves preprocessing the images -
and then store the metadata surrounding the outputs in the `*.images.js`
file such that it can easily be imported.

For example,

admin.images.json
```json
{
    "img1": {
        "path": "/img/admin/img1.jpg",
        "width": 100,
        "height": 100,
        "crop_style": "cover",
        "crop_arguments": {},
        "lazy": true
    }
}
```

will produce

admin.images.js
```js
export default {
    "img1": {
        "target": {
            "settings": {
                "width": 100,
                "height": 100,
                "crop": "cover",
                "crop_settings": {
                    "pre_top_crop": 0,
                    "pre_left_crop": 0,
                    "pre_bottom_crop": 0,
                    "pre_right_crop": 0,
                    "crop_left_percentage": 0.5,
                    "crop_top_percentage": 0.5
                }
            },
            "outputs": {
                "jpeg": [
                    {
                        "width": 100,
                        "height": 100,
                        "url": "/img/admin/img1/100x100.jpeg",
                        "choice": "100"
                    }
                ],
                "webp": [
                    {
                        "width": 100,
                        "height": 100,
                        "url": "/img/admin/img1/100x100.webp",
                        "choice": "lossless"
                    }
                ]
            }
        }
    }
}
```

This will also request and ignore files that have the `*.images.js` extension,
since it is often convenient for development to put a placeholder file in
the source code so that the IDE will recognize the imports. Furthermore, if
the build context is configured with `images.auto_generate_placeholders`,
we will even generate a placeholder file in the source code with the appropriate
type hints.
"""

import dataclasses
from typing import Set
from vanillaplusjs.build.build_context import BuildContext
from vanillaplusjs.build.build_file_result import BuildFileResult
from vanillaplusjs.build.html.manips.images.command import ImageCommand
from vanillaplusjs.build.ioutil import makedirs_safely
from vanillaplusjs.build.scan_file_result import ScanFileResult
import os
import json
from PIL import Image, UnidentifiedImageError
from vanillaplusjs.build.html.manips.images.scanner import scan_command
from vanillaplusjs.build.html.manips.images.exporter import export_command
import vanillaplusjs.build.handlers.hash as hash_handler
from loguru import logger


PLACEHOLDER_FILE = """/**
 * The output for this file is generated via the json file by the same name -
 * this file is just for type hints.
 */

/**
 * Maps from the image name to the image metadata. For each image,
 * contains the settings used to produce that image from the source
 * image as well as the outputs produced.
 *
 * @type {Object.<string, {target: {settings: {width: number, height: number, crop: 'cover', crop_settings: {pre_top_crop: number, pre_left_crop: number, pre_bottom_crop: number, pre_right_crop: number, crop_left_percentage: number, crop_top_percentage: number}}, outputs: Object.<string, Array.<{width: number, height: number, url: string, choice: string}>>}}>}
 */
export default {};
"""


def handles_file(context: BuildContext, relpath: str) -> bool:
    """True if this handler wants to handle the file at the given path
    relative to the root of the project, false otherwise.

    Args:
        context (BuildContext): The build context
        relpath (str): The path to the file relative to the root of the project

    Returns:
        bool: True if this handler wants to handle the file, false otherwise
    """
    return relpath.startswith(os.path.join("src", "public")) and (
        relpath.endswith(".images.json") or relpath.endswith(".images.js")
    )


def scan_file(context: BuildContext, relpath: str) -> ScanFileResult:
    """Scans the given file to determine what this handler would do
    if it were to build it.
    """
    if not handles_file(context, relpath) or relpath.endswith(".images.js"):
        return ScanFileResult(dependencies=[], produces=[])

    with open(os.path.join(context.folder, relpath), "r") as f:
        data = json.load(f)

    if not sanity_check_images_json(context, data, relpath):
        return ScanFileResult(dependencies=[], produces=[])

    path_rel_to_public = relpath[
        len(os.path.join("src", "public")) + len(os.path.sep) :
    ]
    path_rel_to_public_no_ext = path_rel_to_public[: -len(".images.json")]
    out_path = os.path.join("out", "www", path_rel_to_public_no_ext + ".images.js")

    dependencies: Set[str] = set()
    produces = {out_path}
    placeholders = dict()

    placeholder_path = os.path.join(
        "src", "public", path_rel_to_public_no_ext + ".images.js"
    )
    if context.auto_generate_images_js_placeholders and not os.path.exists(
        placeholder_path
    ):
        placeholders[placeholder_path] = PLACEHOLDER_FILE

    command_file_path = os.path.join(context.folder, relpath)
    for _, command_dict in data.items():
        command = ImageCommand(
            path=command_dict["path"],
            width=command_dict["width"],
            height=command_dict["height"],
            crop_style=command_dict.get("crop_style", "cover"),
            crop_arguments=command_dict.get("crop_arguments", dict()),
            lazy=command_dict.get("lazy", True),
        )

        scan_result = scan_command(context, command_file_path, command)
        assert scan_result is not None, f"{command=} should have been verified already"
        dependencies.update(scan_result.dependencies)
        produces.update(scan_result.produces)

    scan_result = hash_handler.scan_file(context, out_path)
    dependencies.update(scan_result.dependencies)
    produces.update(scan_result.produces)
    return ScanFileResult(
        dependencies=list(dependencies),
        produces=list(produces),
        placeholders=placeholders,
    )


def build_file(context: BuildContext, relpath: str) -> BuildFileResult:
    """Builds the given file and returns what we built"""
    if not handles_file(context, relpath) or relpath.endswith(".images.js"):
        return BuildFileResult(children=[], produced=[], reused=[])

    with open(os.path.join(context.folder, relpath), "r") as f:
        data = json.load(f)

    if not sanity_check_images_json(context, data, relpath):
        return BuildFileResult(children=[], produced=[], reused=[])

    path_rel_to_public = relpath[
        len(os.path.join("src", "public")) + len(os.path.sep) :
    ]
    path_rel_to_public_no_ext = path_rel_to_public[: -len(".images.json")]
    out_path = os.path.join("out", "www", path_rel_to_public_no_ext + ".images.js")

    children: Set[str] = set()
    produced: Set[str] = set()
    reused: Set[str] = set()

    output_dictionary = dict()

    command_file_path = os.path.join(context.folder, relpath)
    for command_name, command_dict in data.items():
        command = ImageCommand(
            path=command_dict["path"],
            width=command_dict["width"],
            height=command_dict["height"],
            crop_style=command_dict.get("crop_style", "cover"),
            crop_arguments=command_dict.get("crop_arguments", dict()),
            lazy=command_dict.get("lazy", True),
        )

        metadata, build_result = export_command(context, command_file_path, command)
        children.update(build_result.children)
        produced.update(build_result.produced)
        reused.update(build_result.reused)

        output_dictionary[command_name] = {
            "target": {
                "settings": {
                    "width": metadata.target.settings.width,
                    "height": metadata.target.settings.height,
                    "crop": metadata.target.settings.crop,
                    "crop_settings": dataclasses.asdict(
                        metadata.target.settings.crop_settings
                    ),
                },
                "outputs": dict(
                    (
                        key,
                        [
                            {
                                "width": output.width,
                                "height": output.height,
                                "url": "/" + output.relpath.replace(os.path.sep, "/"),
                                "choice": output.choice,
                            }
                            for output in outputs
                        ],
                    )
                    for key, outputs in metadata.target.outputs.items()
                ),
            }
        }

    makedirs_safely(os.path.join(context.folder, os.path.dirname(out_path)))
    with open(os.path.join(context.folder, out_path), "w", newline="\n") as f:
        f.write("export default ")
        json.dump(output_dictionary, f, sort_keys=True)
        f.write(";\n")

    produced.add(out_path)
    build_result = hash_handler.build_file(context, out_path)
    children.update(build_result.children)
    produced.update(build_result.produced)
    reused.update(build_result.reused)

    return BuildFileResult(
        children=list(children), produced=list(produced), reused=list(reused)
    )


def sanity_check_images_json(context: BuildContext, data: dict, relpath: str) -> bool:
    """Checks that the given data is a valid images json file."""
    ctx = lambda: f"{relpath=}"
    if not isinstance(data, dict):
        logger.warning("[{}] not a dictionary", ctx(), relpath)
        return False

    for img_name, img_target_settings in data.items():
        ctx = lambda: f"{relpath=}, {img_name=}"
        if not isinstance(img_name, str):
            logger.warning("[{}] name is not a string", ctx)
            return False
        if not isinstance(img_target_settings, dict):
            logger.warning("[{}] image target settings are not a dictionary", ctx())
            return False
        path = img_target_settings.get("path")
        if not isinstance(path, str):
            logger.warning("[{}] path is not a string", ctx())
            return False

        if not path.startswith("/"):
            logger.warning("[{}] path is not absolute", ctx())
            return False

        path_rel_to_public = path[1:]
        path_rel_to_root = os.path.join("src", "public", path_rel_to_public)
        if not os.path.exists(os.path.join(context.folder, path_rel_to_root)):
            logger.warning("[{}] path {} does not exist", ctx(), path_rel_to_root)
            return False

        try:
            img = Image.open(os.path.join(context.folder, path_rel_to_root))
            img_width = img.width
            img_height = img.height
            img.close()
        except UnidentifiedImageError:
            logger.warning("[{}] path is not an image", ctx())
            return False

        width = img_target_settings.get("width")
        if not isinstance(width, int) or width <= 0 or width > img_width:
            logger.warning("[{}] width is not an integer or is out of range", ctx())
            return False

        height = img_target_settings.get("height")
        if not isinstance(height, int) or height <= 0 or height > img_height:
            logger.warning("[{}] height is not an integer or is out of range", ctx())
            return False

        if img_target_settings.get("crop_style", "cover") != "cover":
            logger.warning("[{}] crop style is not cover", ctx())
            return False

        crop_settings = img_target_settings.get("crop_settings", dict())
        if not isinstance(crop_settings, dict):
            logger.warning("[{}] crop settings are not a dictionary", ctx())
            return False

        valid_keys = {
            "pre_top_crop",
            "pre_left_crop",
            "pre_right_crop",
            "pre_bottom_crop",
            "crop_left_percentage",
            "crop_top_percentage",
        }
        if any(key not in valid_keys for key in crop_settings):
            logger.warning("[{}] crop settings contain invalid keys", ctx())
            return False

        for key in (
            "pre_top_crop",
            "pre_left_crop",
            "pre_right_crop",
            "pre_bottom_crop",
        ):
            if crop_settings.get(key, 0) < 0:
                logger.warning("[{}] crop setting {} is negative", ctx(), key)
                return False

        if not (0 <= crop_settings.get("crop_left_percentage", 0.5) <= 1):
            logger.warning(
                "[{}] crop setting crop_left_percentage is out of range", ctx()
            )
            return False
        if not (0 <= crop_settings.get("crop_top_percentage", 0.5) <= 1):
            logger.warning(
                "[{}] crop setting crop_top_percentage is out of range", ctx()
            )
            return False

        post_cropped_img_width = (
            img_width
            - crop_settings.get("pre_left_crop", 0)
            - crop_settings.get("pre_right_crop", 0)
        )
        post_cropped_img_height = (
            img_height
            - crop_settings.get("pre_top_crop", 0)
            - crop_settings.get("pre_bottom_crop", 0)
        )
        if post_cropped_img_width < width or post_cropped_img_height < height:
            logger.warning(
                "[{}] crop settings result in an image that is too small ({}x{})",
                ctx(),
                post_cropped_img_width,
                post_cropped_img_height,
            )
            return False

    return True
