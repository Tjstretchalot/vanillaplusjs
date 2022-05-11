from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Optional
from vanillaplusjs.build.build_context import BuildContext
import pytypeutils as tus


@dataclass
class ImageExport:
    """Describes a possible export for a given image format."""

    min_area_px2: Optional[int]
    """The minimum area of the image before this export should be attempted,
    in squared pixels.
    """

    max_area_px2: Optional[int]
    """The maximum area of the image before this export should be attempted,
    in squared pixels.
    """

    preference: int
    """Compared to other image exports within this format, the preference
    for this export. A higher preference means it's more likely we will
    use this export.

    If we have two image exports with a preference of 1 and 2 respectively,
    we will use the second image unless its file size is more than twice
    the size of the first image.
    """

    formatter_kwargs: dict
    """The keyword arguments to pass to the formatter when exporting the
    image.
    """

    def applies_to(self, width: int, height: int) -> bool:
        """Determines if this export applies to target image of the given
        width and height
        """
        area_px2 = width * height
        return (self.min_area_px2 is None or area_px2 >= self.min_area_px2) and (
            self.max_area_px2 is None or area_px2 <= self.max_area_px2
        )


def compare(a: ImageExport, size_a: int, b: ImageExport, size_b: int) -> int:
    """Compares two image exports, based on their preference and size.
    This is rarely used directly, prefer `compare_in_format`

    Args:
        a (ImageExport): The first export.
        size_a (int): The size of the first export.
        b (ImageExport): The second export.
        size_b (int): The size of the second export.

    Returns:
        int: negative if a is preferred, positive if b is preferred, and 0 if
            they are equally preferred.
    """
    return size_a * b.preference - size_b * a.preference


@dataclass
class ImageFormat:
    """Describes a format for exporting images."""

    name: str
    """The name for the format, e.g., jpeg"""

    exports: Dict[str, ImageExport]
    """The exports for this format."""

    minimum_unit_size_bytes: int
    """When considering the score for a particular image, if the file size
    is less than this value, we will score as if it were this size. This avoids
    us choosing to use an low quality image to save a small amount of space.
    """


def compare_in_format(
    fmt: ImageFormat, a: ImageExport, size_a: int, b: ImageExport, size_b: int
) -> int:
    """Compares two image exports in a given format, based on their preference and size.

    Args:
        fmt (ImageFormat): The format to compare in.
        a (ImageExport): The first export.
        size_a (int): The size of the first export.
        b (ImageExport): The second export.
        size_b (int): The size of the second export.

    Returns:
        int: negative if a is preferred, positive if b is preferred, and 0 if
            they are equally preferred.
    """
    size_a = max(size_a, fmt.minimum_unit_size_bytes)
    size_b = max(size_b, fmt.minimum_unit_size_bytes)
    return compare(a, size_a, b, size_b)


@dataclass
class ImageSettings:
    """The settings for producing images"""

    formats: Dict[str, ImageFormat]
    """The formats by name"""

    default_format: str
    """The format to use for the img tag in the picture, aka the fallback format"""

    maximum_resolution: int
    """The maximum resolution to export images to; i.e., if we need a target
    which is WxH, we will export up to 7Wx7H
    """

    resolution_step: Decimal
    """The step size of the resolution.
    For example, with the maximum_resolution of 3 and a resolution step of 1,
    this will generate a 1x, 2x, and 3x version.
    """


def load_image_settings(settings: dict) -> ImageSettings:
    """Loads the image settings from the given dictionary, which is typically
    parsed from a json file.
    """
    tus.check(settings=(settings, dict))
    tus.check(
        settings_formats=(settings.get("formats"), dict),
        settings_default_format=(settings.get("default_format"), str),
        settings_maximum_resolution=(settings.get("maximum_resolution"), int),
        settings_resolution_step=(
            settings.get("resolution_step"),
            (int, float, str, Decimal),
        ),
    )

    formats = {}
    for name, fmt_dict in settings["formats"].items():
        tus.check(
            name=(name, str),
            fmt_dict=(fmt_dict, dict),
            fmt_dict_exports=(fmt_dict.get("exports"), dict),
            fmt_dict_minimum_unit_size_bytes=(
                fmt_dict.get("minimum_unit_size_bytes"),
                int,
            ),
        )

        exports = {}
        for export_name, export_dict in fmt_dict["exports"].items():
            tus.check(
                export_name=(export_name, str),
                export_dict=(export_dict, dict),
            )

            min_area_px2 = export_dict.get("min_area_px2")
            if min_area_px2 is not None:
                tus.check(min_area_px2=(min_area_px2, int))

            max_area_px2 = export_dict.get("max_area_px2")
            if max_area_px2 is not None:
                tus.check(max_area_px2=(max_area_px2, int))

            preference = export_dict.get("preference")
            tus.check(preference=(preference, int))

            formatter_kwargs = export_dict.get("formatter_kwargs", dict())
            tus.check(formatter_kwargs=(formatter_kwargs, dict))

            exports[export_name] = ImageExport(
                min_area_px2=min_area_px2,
                max_area_px2=max_area_px2,
                preference=preference,
                formatter_kwargs=formatter_kwargs,
            )

        formats[name] = ImageFormat(
            name=name,
            exports=exports,
            minimum_unit_size_bytes=fmt_dict["minimum_unit_size_bytes"],
        )

    default_format = settings["default_format"]
    maximum_resolution = settings["maximum_resolution"]
    resolution_step = Decimal(settings["resolution_step"])

    if default_format not in formats:
        raise ValueError(f"Default format {default_format} not found in formats")

    if resolution_step <= 0:
        raise ValueError("resolution_step must be > 0")

    return ImageSettings(
        formats=formats,
        default_format=default_format,
        maximum_resolution=maximum_resolution,
        resolution_step=resolution_step,
    )
