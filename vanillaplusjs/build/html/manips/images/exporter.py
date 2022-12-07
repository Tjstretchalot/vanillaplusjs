"""Facilitates ensuring all the appropriate images are exported."""
import dataclasses
from typing import Dict, List, Literal, Optional, Tuple
from vanillaplusjs.build.build_context import BuildContext
from vanillaplusjs.build.build_file_result import BuildFileResult
from vanillaplusjs.build.file_signature import get_file_signature
from vanillaplusjs.build.html.manips.images.command import ImageCommand
from vanillaplusjs.build.html.manips.images.resolutions import yield_sizes
from vanillaplusjs.build.html.manips.images.settings import (
    ImageExport,
    compare_in_format,
)
from vanillaplusjs.build.ioutil import makedirs_safely
from .cover_fit import cover_fit
import os
import json
from vanillaplusjs.build.html.manips.images.metadata import (
    CropSettingsCover,
    ImageMetadata,
    ImageSource,
    ImageTarget,
    ImageTargetOutput,
    ImageTargetSettings,
    get_target,
    hash_image_settings,
    load_metadata,
    reserve_target_lock_path,
    store_metadata,
)
import shutil
from PIL import Image
from loguru import logger
import time
import concurrent.futures
from pathlib import Path

Image.MAX_IMAGE_PIXELS = 1_000_000_000


def export_command(
    context: BuildContext, command_file_path: str, command: ImageCommand
) -> Tuple[ImageMetadata, BuildFileResult]:
    """Ensures that all the required files are produced for the given command,
    and returns the information surrounding what we needed and what we did.

    Args:
        context (BuildContext): The build context.
        command_file_path (str): The path to the file containing the command.
        command (ImageCommand): The image command to export files for.

    Returns:
        ImageMetadata: The metadata for the image.
        BuildFileResult: The files we needed, produced, and reused
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

    target_id = get_target(context, path_relative_to_public, target)
    assert (
        target_id is not None
    ), f"a target for {path_relative_to_public=} should have been made during scanning"

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

    children: List[str] = []
    reused: List[str] = []
    produced: List[str] = []

    children.append(path_relative_to_root)

    lock_file = os.path.relpath(
        reserve_target_lock_path(context, path_relative_to_public), context.folder
    )
    if os.path.exists(
        os.path.join(
            context.folder, target_art_folder_relative_to_root, "metadata.json"
        )
    ):
        reused.append(os.path.join(target_art_folder_relative_to_root, "metadata.json"))
        reused.append(os.path.join(source_art_folder_relative_to_root, "counter.txt"))
        reused.append(
            os.path.join(target_art_folder_relative_to_root, "placeholder.json")
        )
        with open(
            os.path.join(
                context.folder, target_art_folder_relative_to_root, "metadata.json"
            )
        ) as f:
            metadata_dict = json.load(f)
        metadata = load_metadata(metadata_dict)

        we_are_first = True
        for _, output_list in metadata.target.outputs.items():
            for output in output_list:
                reused.append(os.path.join("artifacts", output.relpath))
                out_file = os.path.join("out", "www", output.relpath)
                if os.path.exists(os.path.join(context.folder, out_file)):
                    we_are_first = False
                    reused.append(out_file)
                else:
                    produced.append(out_file)
                    makedirs_safely(
                        os.path.dirname(os.path.join(context.folder, out_file))
                    )

                    if context.symlinks:
                        os.symlink(
                            os.path.join(context.artifacts_folder, output.relpath),
                            os.path.join(context.folder, out_file),
                        )
                    else:
                        shutil.copy(
                            os.path.join(context.artifacts_folder, output.relpath),
                            os.path.join(context.folder, out_file),
                        )

        if we_are_first:
            makedirs_safely(os.path.dirname(os.path.join(context.folder, lock_file)))
            Path(os.path.join(context.folder, lock_file)).touch()
            produced.append(lock_file)
        else:
            reused.append(lock_file)

        return metadata, BuildFileResult(
            children=children,
            produced=produced,
            reused=reused,
        )

    produced.append(os.path.join(target_art_folder_relative_to_root, "metadata.json"))
    produced.append(os.path.join(source_art_folder_relative_to_root, "counter.txt"))
    produced.append(
        os.path.join(target_art_folder_relative_to_root, "placeholder.json")
    )
    produced.append(lock_file)

    image = Image.open(os.path.join(context.public_folder, path_relative_to_public))
    image_width = image.width
    image_height = image.height
    image.close()
    del image

    with open(
        os.path.join(context.out_folder, "www", path_relative_to_public + ".hash")
    ) as f:
        contents_hash = f.read()

    settings_hash = hash_image_settings(context.image_settings)
    source = ImageSource(
        path=path_relative_to_root,
        width=image_width,
        height=image_height,
        contents_hash=contents_hash,
    )
    outputs: Dict[str, List[ImageTargetOutput]] = dict()

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures: List[concurrent.futures.Future] = []
        for out_width, out_height in yield_sizes(
            context, image_width, image_height, command.width, command.height
        ):
            for format_name, format_settings in context.image_settings.formats.items():
                for export_name, export_settings in format_settings.exports.items():
                    if not export_settings.applies_to(out_width, out_height):
                        continue
                    futures.append(
                        executor.submit(
                            produce_image,
                            os.path.join(context.folder, path_relative_to_root),
                            os.path.join(
                                context.folder,
                                target_art_folder_relative_to_root,
                                f"{out_width}x{out_height}-{export_name}.{format_name}",
                            ),
                            out_width,
                            out_height,
                            command.crop_style,
                            crop_settings,
                            format_name,
                            export_settings.formatter_kwargs,
                        )
                    )

        concurrent.futures.wait(futures, return_when=concurrent.futures.ALL_COMPLETED)
        for future in futures:
            if future.exception() is not None:
                raise future.exception()
            assert future.done()

    for out_width, out_height in yield_sizes(
        context, image_width, image_height, command.width, command.height
    ):
        for format_name, format_settings in context.image_settings.formats.items():
            best_export: Optional[ImageExport] = None
            best_export_name: Optional[str] = None
            best_export_size: Optional[int] = None
            best_export_path: Optional[str] = None
            for export_name, export_settings in format_settings.exports.items():
                if not export_settings.applies_to(out_width, out_height):
                    continue
                export_path = os.path.join(
                    context.folder,
                    target_art_folder_relative_to_root,
                    f"{out_width}x{out_height}-{export_name}.{format_name}",
                )
                export_size = os.lstat(export_path).st_size
                if (
                    best_export is None
                    or compare_in_format(
                        format_settings,
                        best_export,
                        best_export_size,
                        export_settings,
                        export_size,
                    )
                    > 0
                ):
                    if best_export_path is not None:
                        os.remove(best_export_path)
                    best_export = export_settings
                    best_export_name = export_name
                    best_export_size = export_size
                    best_export_path = export_path
                else:
                    os.remove(export_path)

            if best_export is None:
                continue

            desired_filename = f"{out_width}x{out_height}.{format_name}"
            desired_path = os.path.join(
                context.folder,
                target_art_folder_relative_to_root,
                desired_filename,
            )
            os.rename(best_export_path, desired_path)

            output_list = outputs.get(format_name)
            if output_list is None:
                output_list = []
                outputs[format_name] = output_list

            output_list.append(
                ImageTargetOutput(
                    width=out_width,
                    height=out_height,
                    relpath=os.path.join(
                        os.path.relpath(
                            target_art_folder_relative_to_root, "artifacts"
                        ),
                        f"{out_width}x{out_height}.{format_name}",
                    ),
                    choice=best_export_name,
                )
            )
            produced.append(os.path.relpath(desired_path, context.folder))

            out_path_relative_to_root = os.path.join(
                target_out_folder_relative_to_root, desired_filename
            )
            makedirs_safely(
                os.path.join(context.folder, target_out_folder_relative_to_root)
            )
            if context.symlinks:
                os.symlink(
                    desired_path,
                    os.path.join(context.folder, out_path_relative_to_root),
                )
            else:
                shutil.copy(
                    desired_path,
                    os.path.join(context.folder, out_path_relative_to_root),
                )

            produced.append(out_path_relative_to_root)

    metadata = ImageMetadata(
        settings_hash=settings_hash,
        source=source,
        target=ImageTarget(
            settings=target,
            outputs=outputs,
        ),
    )

    with open(
        os.path.join(
            context.folder, target_art_folder_relative_to_root, "metadata.json"
        ),
        "w",
    ) as f:
        json.dump(store_metadata(metadata), f, indent=2)

    return metadata, BuildFileResult(
        children=children,
        reused=reused,
        produced=produced,
    )


def produce_image(
    src_file: str,
    dst_file: str,
    width: int,
    height: int,
    crop_style: Literal["cover"],
    crop_settings: CropSettingsCover,
    format: str,
    formatter_kwargs: dict,
) -> None:
    """Synchronously loads the given source file, processes it according to
    the given settings, and saves the result to the given destination file.

    Args:
        src_file (str): The file containing the image to process.
        dst_file (str): The file to save the processed image to.
        width (int): The width to resize the image to.
        height (int): The height to resize the image to.
        crop_style (Literal["cover"]): The crop style to use.
        crop_settings (CropSettingsCover): The crop settings to use.
        format (str): The format to save the image in, e.g., "jpeg"
        formatter_kwargs (dict): The keyword arguments to pass to the formatter.
    """
    assert crop_style == "cover", f"crop style {crop_style} not supported"
    image = Image.open(src_file)

    (x, y, w, h) = cover_fit(
        source_width=image.width,
        source_height=image.height,
        dest_width=width,
        dest_height=height,
        **dataclasses.asdict(crop_settings),
    )

    if x != 0 or y != 0 or w != image.width or h != image.height:
        image = image.crop((x, y, x + w, y + h))

    if image.width != width or image.height != height:
        image = image.resize((width, height), Image.Resampling.LANCZOS)

    logger.debug("Exporting to {}", dst_file)
    makedirs_safely(os.path.dirname(dst_file))
    now = time.perf_counter()
    image.save(dst_file, format=format, **formatter_kwargs)
    time_taken = time.perf_counter() - now
    logger.debug("Exported to {} in {:.3f}s", dst_file, time_taken)
