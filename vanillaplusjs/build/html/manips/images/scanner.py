from typing import List
from vanillaplusjs.build.build_context import BuildContext
from vanillaplusjs.build.html.manips.images.command import ImageCommand
from vanillaplusjs.build.html.manips.images.metadata import (
    CropSettingsCover,
    ImageTargetSettings,
    get_or_reserve_target,
    reserve_target_lock_path,
)
from vanillaplusjs.build.html.manips.images.resolutions import yield_sizes
from vanillaplusjs.build.scan_file_result import ScanFileResult
import os
from PIL import Image

Image.MAX_IMAGE_PIXELS = 1_000_000_000


def scan_command(
    context: BuildContext, command_file_path: str, command: ImageCommand
) -> ScanFileResult:
    """Determines what dependencies are required for the given image
    command, and what files we will produce.

    Args:
        context (BuildContext): The build context.
        command_file_path (str): The path to the file containing the command.
        command (ImageCommand): The image command to scan.

    Returns:
        ScanFileResult: The result of scanning the command.
    """
    path_relative_to_root = command.source_path_relative_to_root(
        context, command_file_path
    )
    path_relative_to_public = path_relative_to_root[
        len(os.path.join("src", "public")) + len(os.path.sep) :
    ]

    crop_settings = CropSettingsCover(**command.crop_arguments)
    target = ImageTargetSettings(
        width=command.width,
        height=command.height,
        crop=command.crop_style,
        crop_settings=crop_settings,
    )

    target_id = get_or_reserve_target(context, path_relative_to_public, target)
    path_rel_to_public_no_ext = os.path.splitext(path_relative_to_public)[0]
    source_art_folder_relative_to_root = os.path.join(
        "artifacts",
        path_rel_to_public_no_ext,
    )
    target_art_folder_relative_to_root = os.path.join(
        source_art_folder_relative_to_root,
        str(target_id),
    )
    target_out_folder_relative_to_root = os.path.join(
        "out", "www", path_rel_to_public_no_ext, str(target_id)
    )

    dependencies: List[str] = []
    produces: List[str] = []

    dependencies.append(path_relative_to_root)
    produces.append(os.path.join(target_art_folder_relative_to_root, "metadata.json"))
    produces.append(os.path.join(source_art_folder_relative_to_root, "counter.txt"))
    produces.append(
        os.path.join(target_art_folder_relative_to_root, "placeholder.json")
    )
    produces.append(reserve_target_lock_path(context, path_relative_to_public))

    image = Image.open(os.path.join(context.public_folder, path_relative_to_public))
    image_width = image.width
    image_height = image.height
    image.close()

    for out_width, out_height in yield_sizes(
        context, image_width, image_height, command.width, command.height
    ):
        for format_name in context.image_settings.formats.keys():
            file_name = f"{out_width}x{out_height}.{format_name}"
            produces.append(os.path.join(target_art_folder_relative_to_root, file_name))
            produces.append(os.path.join(target_out_folder_relative_to_root, file_name))

    return ScanFileResult(
        dependencies=dependencies,
        produces=produces,
    )
