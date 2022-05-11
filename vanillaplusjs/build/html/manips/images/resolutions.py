from decimal import Decimal
from typing import Generator, Tuple
from vanillaplusjs.build.build_context import BuildContext


def yield_resolutions(
    context: BuildContext,
    src_width: int,
    src_height: int,
    dst_width: int,
    dst_height: int,
) -> Generator[Decimal, None, None]:
    """Yields the resolutions to export an image of the given source
    size targetting the given destination size.

    For example, if the source image is 500x500 but we are targeting
    100x100, we might produce a 1x, 2x, 3x, 4x, and 5x version of the
    image.

    The maximum resolution and step size is configured in the build
    context's image settings.

    Args:
        context (BuildContext): The build context.
        src_width (int): The width of the source image.
        src_height (int): The height of the source image.
        dst_width (int): The width of the destination image.
        dst_height (int): The height of the destination image.

    Yields:
        Decimal: The resolution to export the image at.
    """
    resolution = Decimal(1)
    while (
        src_width >= (dst_width * resolution)
        and src_height >= (dst_height * resolution)
        and resolution <= context.image_settings.maximum_resolution
    ):
        yield resolution
        resolution += context.image_settings.resolution_step


def yield_sizes(
    context: BuildContext,
    src_width: int,
    src_height: int,
    dst_width: int,
    dst_height: int,
) -> Generator[Tuple[int, int], None, None]:
    """Analogous to yield_resolutions, but yields the sizes to export
    an image of the given source size targetting the given destination
    size, instead of the multiple of the base resolution.
    """
    for resolution in yield_resolutions(
        context, src_width, src_height, dst_width, dst_height
    ):
        yield int(dst_width * resolution), int(dst_height * resolution)
