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
from decimal import Decimal
from vanillaplusjs.build.build_context import BuildContext
from typing import Dict, Literal, List, Optional, Union
import os
import json
import fasteners
from vanillaplusjs.build.handlers.hash import calculate_hash
from vanillaplusjs.build.html.manips.images.settings import ImageSettings
from loguru import logger

from vanillaplusjs.build.ioutil import makedirs_safely


@dataclass(frozen=True)
class ImageSource:
    """The source for an exported image"""

    path: str
    """The path to the image file relative to the public folder"""

    width: int
    """The width of the image"""

    height: int
    """The height of the image"""

    contents_hash: str
    """The hash of the image file"""


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


def load_image_target_settings(serd: dict) -> ImageTargetSettings:
    return ImageTargetSettings(
        width=serd["width"],
        height=serd["height"],
        crop=serd["crop"],
        crop_settings=CropSettingsCover(
            pre_top_crop=serd["crop_settings"]["pre_top_crop"],
            pre_left_crop=serd["crop_settings"]["pre_left_crop"],
            pre_right_crop=serd["crop_settings"]["pre_right_crop"],
            pre_bottom_crop=serd["crop_settings"]["pre_bottom_crop"],
            crop_left_percentage=serd["crop_settings"]["crop_left_percentage"],
            crop_top_percentage=serd["crop_settings"]["crop_top_percentage"],
        ),
    )


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


@dataclass(frozen=True)
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
            path=serd["source"]["path"].replace("/", os.path.sep),
            width=serd["source"]["width"],
            height=serd["source"]["height"],
            contents_hash=serd["source"]["contents_hash"],
        ),
        target=ImageTarget(
            settings=load_image_target_settings(serd["target"]["settings"]),
            outputs=dict(
                (
                    key,
                    [
                        ImageTargetOutput(
                            width=output["width"],
                            height=output["height"],
                            relpath=output["relpath"].replace("/", os.path.sep),
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
    res = dataclasses.asdict(metadata)
    res["source"]["path"] = res["source"]["path"].replace(os.path.sep, "/")
    for target in res["target"]["outputs"].values():
        for output in target:
            output["relpath"] = output["relpath"].replace(os.path.sep, "/")
    return res


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

    precomputed_hash_path = os.path.join(context.out_folder, "www", relpath + ".hash")
    try:
        with open(precomputed_hash_path, "r") as f:
            contents_hash = f.read()
    except FileNotFoundError:
        logger.debug(
            "No precomputed hash available for {} (expected at {}), calculating on demand",
            os.path.join(context.public_folder, relpath),
            precomputed_hash_path,
        )
        contents_hash = calculate_hash(os.path.join(context.public_folder, relpath))

    settings_hash = hash_image_settings(context.image_settings)

    scanner = os.scandir(art_path)
    try:
        while True:
            try:
                entry = next(scanner)
            except StopIteration:
                break

            if not entry.is_dir():
                continue

            if not os.path.exists(os.path.join(entry.path, "metadata.json")):
                lock_path = reserve_target_lock_path(context, relpath)
                makedirs_safely(os.path.dirname(lock_path))
                with fasteners.InterProcessLock(lock_path):
                    if os.path.exists(os.path.join(entry.path, "placeholder.json")):
                        with open(
                            os.path.join(entry.path, "placeholder.json"), "r"
                        ) as f:
                            placeholder = load_image_target_settings(json.load(f))
                        if placeholder == target:
                            return int(entry.name)
                continue

            with open(os.path.join(entry.path, "metadata.json"), "r") as f:
                entry_metadata = load_metadata(json.load(f))

            if entry_metadata.settings_hash != settings_hash:
                logger.debug(
                    "{} is not a match for {}; the settings hash is {} but should be {}",
                    entry.path,
                    relpath,
                    entry_metadata.settings_hash,
                    settings_hash,
                )
                continue
            if entry_metadata.source.contents_hash != contents_hash:
                logger.debug(
                    "{} is not a match for {}; the source hash is {} but should be {}",
                    entry.path,
                    relpath,
                    entry_metadata["source"]["contents_hash"],
                    contents_hash,
                )
                continue
            if entry_metadata.target.settings != target:
                logger.debug(
                    "{} is not a match for {}; the target settings are {} but should be {}",
                    entry.path,
                    relpath,
                    entry_metadata.target.settings,
                    target,
                )
                continue

            return int(entry.name)

        return None
    finally:
        scanner.close()


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
    makedirs_safely(os.path.dirname(lock_path))
    makedirs_safely(art_path)
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
        makedirs_safely(entry_path)
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
        result = overflow(result * prime + stable_hash(format_name))

        sorted_export_names = sorted(format.exports.keys())
        for export_name in sorted_export_names:
            export = format.exports[export_name]
            result = overflow(result * prime + stable_hash(export_name))
            result = overflow(result * prime + stable_hash(export.min_area_px2))
            result = overflow(result * prime + stable_hash(export.max_area_px2))
            result = overflow(result * prime + stable_hash(export.preference))

            sorted_formatter_kwarg_names = sorted(export.formatter_kwargs.keys())
            for kwarg_name in sorted_formatter_kwarg_names:
                kwarg = export.formatter_kwargs[kwarg_name]
                result = overflow(result * prime + stable_hash(kwarg_name))
                if isinstance(kwarg, str):
                    result = overflow(result * prime + stable_hash(kwarg))
                else:
                    result = overflow(result * prime + stable_hash(kwarg))

        result = overflow(result * prime + stable_hash(format.minimum_unit_size_bytes))

    result = overflow(result * prime + stable_hash(settings.default_format))
    result = overflow(result * prime + stable_hash(settings.maximum_resolution))
    result = overflow(result * prime + stable_hash(settings.resolution_step))
    return result


def overflow(n: int) -> int:
    """Overflows the integer as if it were a 64-bit unsigned integer."""
    return n & 0xFFFFFFFFFFFFFFFF


def stable_hash(v: Optional[Union[int, float, Decimal, str, bool]]) -> int:
    """Provides a stable hash of v"""
    if v is None:
        return 447684351148253

    if v is True:
        return 945172902943441

    if v is False:
        return 596202892359953

    if isinstance(v, int):
        return v

    if isinstance(v, float):
        return overflow(31 * hash_str(str(v)) + 843027630870857)

    if isinstance(v, Decimal):
        return overflow(31 * hash_str(str(v)) + 563112335098849)

    if isinstance(v, str):
        return hash_str(v)

    raise ValueError(f"Unsupported type: {type(v)}")


def hash_str(s: str) -> int:
    """Produces a stable hash for the given string."""
    prime = 31
    result = 1

    for c in s:
        result = overflow(result * prime + ord(c))

    return result
