from dataclasses import dataclass
import os


@dataclass(frozen=True)
class FileSignature:
    """Describes a files signature. If a file differs in any of these fields
    from the previous build, it will be rebuilt.
    """

    mtime: float
    """When the files content was last modified, typically to at least the nearest
    second (truncated).
    """

    filesize: int
    """The size of the file in bytes"""

    inode: int
    """Refers to where the physical file is located. If the system does not
    support inodes, this will be 0.
    """


def get_file_signature(file: str) -> FileSignature:
    """Gets the file signature for the given file.

    Args:
        file (str): The path to the file to get the signature of

    Returns:
        FileSignature: The file signature
    """
    stats = os.lstat(file)

    try:
        inode = stats.st_ino
    except AttributeError:
        inode = 0

    return FileSignature(
        mtime=stats.st_mtime,
        filesize=stats.st_size,
        inode=inode,
    )
