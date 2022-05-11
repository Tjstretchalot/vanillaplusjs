"""This module describes the stable metadata we keep on images
in the artifacts folder. It is particularly important that we recall that unless
we guarrantee that if two different files produce the same target path, either
one of them would be sufficient to produce that path, then the rebuilder will
not be able to help us determine what information is no longer necessary, and
hence that file will have a tendency to bloat.

As a specific example, if we stored a list of targets in a single json file,
we couldn't reuse that file unless we needed that _exact_ list of targets.
Otherwise, if we were to reproduce it, we wouldn't produce the same file (we
would have to change the list of targets).

Hence, we instead choose to specify exactly one target per metadata file.

The only exception we make is the `counter.txt` which contains a single number
we increment when we want a new folder, for performance (compared to scanning)
and convenience of testing (compared to random identifiers or hashes).

Note that scanning naively would not work since the scan step for all files
occurs before the build step, though it could be accomplished by writing
empty folders during the scan step, and handling these specially.
"""
from dataclasses import dataclass
import dataclasses
from vanillaplusjs.build.build_context import BuildContext
from vanillaplusjs.build.file_signature import FileSignature, get_file_signature
from typing import Dict, Literal, List, Optional
import os
import json
import fasteners
from vanillaplusjs.build.html.manips.images.settings import ImageSettings
from loguru import logger


@dataclass(frozen=True)
class ImageSource:
    """The source for an exported image"""

    path: str
    """The path to the image file relative to the public folder"""

    width: int
    """The width of the image"""

    height: int
    """The height of the image"""

    signature: FileSignature
    """The signature of the image file"""


@dataclass(frozen=True)
class CropSettingsCover:
    """The crop settings for the `cover` crop style"""

    pre_top_crop: int = 0
    """The number of pixels to crop from the top of the image prior to
    applying the standard cropping rules.
    """

    pre_left_crop: int = 0
    """The number of pixels to crop from the left of the image prior to
    applying the standard cropping rules.
    """

    pre_right_crop: int = 0
    """The number of pixels to crop from the right of the image prior to
    applying the standard cropping rules.
    """

    pre_bottom_crop: int = 0
    """The number of pixels to crop from the bottom of the image prior to
    applying the standard cropping rules.
    """

    crop_left_percentage: float = 0.5
    """When we need to crop to reduce the width, how much we take from the
    left (the remainder is taken from the right).
    """

    crop_top_percentage: float = 0.5
    """When we need to crop to reduce the height, how much we take from the
    top (the remainder is taken from the bottom).
    """


@dataclass(frozen=True)
class ImageTargetSettings:
    """The settings to produce an export for an image source."""

    width: int
    """The width of the target image"""

    height: int
    """The height of the target image"""

    crop: Literal["cover"]
    """The crop style to use when cropping the image"""

    crop_settings: CropSettingsCover
    """The arguments to the crop function.
    """


@dataclass(frozen=True)
class ImageTargetOutput:
    """Describes one artifact we produced when generating an image target from
    an image source.
    """

    width: int
    """The width of the artifact in pixels"""

    height: int
    """The height of the artifact in pixels"""

    relpath: str
    """The path to the artifact relative to the artifacts folder"""

    choice: str
    """The choice of compression used. This is a key in the
    corresponding ImageFormat in the settings.
    """


@dataclass
class ImageTarget:
    """A target we needed when producing an image."""

    settings: ImageTargetSettings
    """The settings to produce an export for an image source.
    """

    outputs: Dict[str, List[ImageTargetOutput]]
    """The outputs produced using those settings. The keys are the
    file format of the output, the values are the outputs in that
    file format.
    """


@dataclass
class ImageMetadata:
    """The metadata for the targets and corresponding artifacts produced
    from a single image. Typically stored in a JSON file adjacent to the
    artifacts.
    """

    settings_hash: int
    """The hash of the ImageSettings on the BuildContext when these
    settings were generated.
    """

    source: ImageSource
    """The source image"""

    target: ImageTarget
    """The target image"""


def load_metadata(serd: dict) -> ImageMetadata:
    """Loads the metadata from a JSON serialized dict."""
    return ImageMetadata(
        settings_hash=serd["settings_hash"],
        source=ImageSource(
            path=serd["source"]["path"],
            width=serd["source"]["width"],
            height=serd["source"]["height"],
            signature=FileSignature(
                mtime=serd["source"]["signature"]["mtime"],
                filesize=serd["source"]["signature"]["filesize"],
                inode=serd["source"]["signature"]["inode"],
            ),
        ),
        target=ImageTarget(
            settings=ImageTargetSettings(
                width=serd["target"]["settings"]["width"],
                height=serd["target"]["settings"]["height"],
                crop=serd["target"]["settings"]["crop"],
                crop_settings=CropSettingsCover(
                    pre_top_crop=serd["target"]["settings"]["crop_settings"][
                        "pre_top_crop"
                    ],
                    pre_left_crop=serd["target"]["settings"]["crop_settings"][
                        "pre_left_crop"
                    ],
                    pre_right_crop=serd["target"]["settings"]["crop_settings"][
                        "pre_right_crop"
                    ],
                    pre_bottom_crop=serd["target"]["settings"]["crop_settings"][
                        "pre_bottom_crop"
                    ],
                    crop_left_percentage=serd["target"]["settings"]["crop_settings"][
                        "crop_left_percentage"
                    ],
                    crop_top_percentage=serd["target"]["settings"]["crop_settings"][
                        "crop_top_percentage"
                    ],
                ),
            ),
            outputs=dict(
                (
                    key,
                    [
                        ImageTargetOutput(
                            width=output["width"],
                            height=output["height"],
                            relpath=output["relpath"],
                            choice=output["choice"],
                        )
                        for output in value
                    ],
                )
                for key, value in serd["target"]["outputs"].items()
            ),
        ),
    )


def store_metadata(metadata: ImageMetadata) -> dict:
    """Stores the metadata in a JSON-serializable dict."""
    return dataclasses.asdict(metadata)


def get_target(
    context: BuildContext,
    relpath: str,
    target: ImageTargetSettings,
) -> Optional[int]:
    """Looks up the ID of the given target settings, if they already
    exist in the build context.

    If the relpath is, for example, "img/test.jpg", then the source
    image is available at "src/public/img/test.jpg" and the expected
    artifacts folder is "artifacts/img/test". If this returns "1",
    then the folder which contains the artifacts for the desired
    target is "artifacts/img/test/1".

    This will only return a target if one already exists AND the
    source image signature matches the signature it had at the time
    the target was created.

    Args:
        context (BuildContext): The build context to use.
        relpath (str): The path to the image relative to the public folder.
        target (ImageTargetSettings): The target settings to look up.

    Returns:
        (int, None): The ID of the target, or None if it doesn't exist.
    """
    if not os.path.exists(os.path.join(context.public_folder, relpath)):
        return None

    relpath_without_ext = os.path.splitext(relpath)[0]
    art_path = os.path.join(context.artifacts_folder, relpath_without_ext)
    if not os.path.exists(art_path):
        return None

    source_signature = get_file_signature(os.path.join(context.public_folder, relpath))
    source_signature_as_dict = dataclasses.asdict(source_signature)
    target_as_dict = dataclasses.asdict(target)
    settings_hash = hash_image_settings(context.image_settings)

    for entry in os.scandir(art_path):
        if not entry.is_dir():
            continue

        if not os.path.exists(os.path.join(entry.path, "metadata.json")):
            lock_path = reserve_target_lock_path(context, relpath)
            os.makedirs(os.path.dirname(lock_path), exist_ok=True)
            with fasteners.InterProcessLock(lock_path):
                if os.path.exists(os.path.join(entry.path, "placeholder.json")):
                    with open(os.path.join(entry.path, "placeholder.json"), "r") as f:
                        placeholder = json.load(f)
                    if placeholder == target_as_dict:
                        return int(entry.name)
            continue

        with open(os.path.join(entry.path, "metadata.json"), "r") as f:
            entry_metadata = json.load(f)

        if entry_metadata["settings_hash"] != settings_hash:
            continue
        if entry_metadata["source"]["signature"] != source_signature_as_dict:
            continue
        if entry_metadata["target"]["settings"] != target_as_dict:
            continue

        return int(entry.name)

    return None


def reserve_target_lock_path(context: BuildContext, relpath: str) -> str:
    relpath_without_ext = os.path.splitext(relpath)[0]
    return os.path.join(
        context.out_folder, "locks", relpath_without_ext, "reserve_target.lock"
    )


def reserve_target(
    context: BuildContext, relpath: str, target: ImageTargetSettings
) -> int:
    """Assigns a new unused id for the given source image, and prevents
    it from being reserved again.
    """
    relpath_without_ext = os.path.splitext(relpath)[0]
    art_path = os.path.join(context.artifacts_folder, relpath_without_ext)
    lock_path = reserve_target_lock_path(context, relpath)
    os.makedirs(os.path.dirname(lock_path), exist_ok=True)
    os.makedirs(art_path, exist_ok=True)
    with fasteners.InterProcessLock(lock_path):
        try:
            with open(os.path.join(art_path, "counter.txt"), "r") as f:
                counter = int(f.read())
        except FileNotFoundError:
            counter = 0

        counter = counter + 1

        with open(os.path.join(art_path, "counter.txt"), "w") as f:
            f.write(str(counter))

        entry_path = os.path.join(art_path, str(counter))
        placeholder_path = os.path.join(entry_path, "placeholder.json")
        os.makedirs(entry_path, exist_ok=True)
        with open(placeholder_path, "w") as f:
            json.dump(dataclasses.asdict(target), f)

        return counter


def get_or_reserve_target(
    context: BuildContext,
    relpath: str,
    target: ImageTargetSettings,
) -> int:
    """If the target already exists, returns its ID. Otherwise, reserves
    a new ID for the target.
    """
    target_id = get_target(context, relpath, target)
    if target_id is None:
        target_id = reserve_target(context, relpath, target)
    return target_id


def hash_image_settings(settings: ImageSettings) -> int:
    """Produces a stable hash for the given image settings."""
    prime = 31
    result = 1

    sorted_formats = sorted(settings.formats.keys())
    for format_name in sorted_formats:
        format = settings.formats[format_name]
        result = overflow(result * prime + hash(format_name))

        sorted_export_names = sorted(format.exports.keys())
        for export_name in sorted_export_names:
            export = format.exports[export_name]
            result = overflow(result * prime + hash(export_name))
            result = overflow(result * prime + hash(export.min_area_px2))
            result = overflow(result * prime + hash(export.max_area_px2))
            result = overflow(result * prime + hash(export.preference))

            formatter_kwarg_names = sorted(export.formatter_kwargs.keys())
            for kwarg_name in formatter_kwarg_names:
                kwarg = export.formatter_kwargs[kwarg_name]
                result = overflow(result * prime + hash(kwarg_name))
                result = overflow(result * prime + hash(kwarg))

        result = overflow(result * prime + hash(format.minimum_unit_size_bytes))

    result = overflow(result * prime + hash(settings.default_format))
    result = overflow(result * prime + hash(settings.maximum_resolution))
    result = overflow(result * prime + hash(settings.resolution_step))
    return result


def overflow(n: int) -> int:
    """Overflows the integer as if it were a 64-bit unsigned integer."""
    return n & 0xFFFFFFFFFFFFFFFF
