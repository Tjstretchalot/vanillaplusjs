from decimal import Decimal
from typing import Tuple, Union


def cover_fit(
    source_width: int,
    source_height: int,
    dest_width: int,
    dest_height: int,
    crop_left_percentage: Union[float, Decimal] = 0.5,
    crop_top_percentage: Union[float, Decimal] = 0.5,
    pre_top_crop: int = 0,
    pre_left_crop: int = 0,
    pre_bottom_crop: int = 0,
    pre_right_crop: int = 0,
) -> Tuple[int, int, int, int]:
    """Computes the destination rectangle for an object-fit cover image
    which needs to fit in a rectangle of the given size.

    MDN:
    The replaced content is sized to maintain its aspect ratio while filling the
    element's entire content box. If the object's aspect ratio does not match
    the aspect ratio of its box, then the object will be clipped to fit.

    Args:
        source_width (int): The width of the actual image
        source_height (int): The height of the actual image
        dest_width (int): The width we need the image to be
        dest_height (int): The height we need the image to be
        crop_left_percentage (float): If we need to crop the image to make
            it thinner, how much of the crop should be taken from the left
            side. At 0.5 we crop evenly from the left and the right. At 0
            we crop exclusively from the right.
        crop_top_percentage (float): If we need to crop the image to make
            it shorter, how much of the crop should be taken from the top
            side. At 0.5 we crop evenly from the top and the bottom. At 0
            we crop exclusively from the bottom.
        pre_top_crop (int): The minimum amount of pixels to crop from the
            top. Essentially you can think of this as cropping this amount
            of the top before performing the cover fit.
        pre_left_crop (int): The minimum amount of pixels to crop from the
            left. Essentially you can think of this as cropping this amount
            of the left before performing the cover fit.
        pre_bottom_crop (int): The minimum amount of pixels to crop from the
            bottom. Essentially you can think of this as cropping this amount
            of the bottom before performing the cover fit.
        pre_right_crop (int): The minimum amount of pixels to crop from the
            right. Essentially you can think of this as cropping this amount
            of the right before performing the cover fit.

    Returns:
        (int, int, int, int): (x, y, w, h) - the rectangle of the source
            image to use.

    Raises:
        ValueError: If the crop is impossible (such as if the source image
            is too small).
    """
    crop_left_percentage = Decimal(crop_left_percentage)
    crop_top_percentage = Decimal(crop_top_percentage)

    if (
        pre_top_crop != 0
        or pre_left_crop != 0
        or pre_bottom_crop != 0
        or pre_right_crop != 0
    ):
        # perform the cover fit on the smaller image
        if source_width - pre_left_crop - pre_right_crop <= 0:
            raise ValueError(
                f"After cropping an image of {source_width=} by {pre_left_crop=} and {pre_right_crop=} there is nothing left"
            )
        if source_height - pre_top_crop - pre_bottom_crop <= 0:
            raise ValueError(
                f"After cropping an image of {source_height=} by {pre_top_crop=} and {pre_bottom_crop=} there is nothing left"
            )

        relative_crop = cover_fit(
            source_width=source_width - pre_left_crop - pre_right_crop,
            source_height=source_height - pre_top_crop - pre_bottom_crop,
            dest_width=dest_width,
            dest_height=dest_height,
            crop_left_percentage=crop_left_percentage,
            crop_top_percentage=crop_top_percentage,
        )

        return (
            pre_left_crop + relative_crop[0],
            pre_top_crop + relative_crop[1],
            relative_crop[2],
            relative_crop[3],
        )

    source_ratio = source_width / source_height
    dest_ratio = dest_width / dest_height

    if source_ratio > dest_ratio:
        # The source is wider than the destination; crop the left and right
        # sides equally to the correct aspect ratio
        source_resolution = source_height / dest_height
        crop_width = round(dest_width * source_resolution)
        crop_x = int((source_width - crop_width) * crop_left_percentage)
        return (crop_x, 0, crop_width, source_height)
    elif source_ratio < dest_ratio:
        # The source is taller than the destination; crop the top and bottom
        # sides equally to the correct aspect ratio
        source_resolution = source_width / dest_width
        crop_height = round(dest_height * source_resolution)
        crop_y = int((source_height - crop_height) * crop_top_percentage)
        return (0, crop_y, source_width, crop_height)

    # it's the exact same ratio, just resize
    return (0, 0, source_width, source_height)
