from dataclasses import dataclass
import os
from typing import Dict, List, Optional, TYPE_CHECKING, Union

from vanillaplusjs.build.file_signature import FileSignature

if TYPE_CHECKING:
    from vanillaplusjs.build.css.manips.icons.settings import IconSettings
    from vanillaplusjs.build.html.manips.images.settings import ImageSettings


@dataclass
class ExternalFile:
    """Describes a file which is not distributed with the source repository
    and hence we may need to download if it does not exist.
    """

    relpath: str
    """The path to where the file should be relative to the project root"""

    url: str
    """The URL to download the file from"""

    integrity: str
    """The expected hash of the file, in the form digest_type-value, e.g.,
    sha384-xxx. You usually find this value in the same place you found
    the cdn link.

    For example:

    <link href="https://example.com/my-file.css" rel="stylesheet" integrity="sha384-asdf" crossorigin="anonymous">

    has the integrity "sha384-asdf"
    """


@dataclass
class ExternalFileState:
    """The state of a single external file that we store to avoid an
    expensive hashing step to determine if its been changed.
    """

    relpath: str
    """The path to the external file relative to the project root"""

    integrity: str
    """The hash of the file that we downloaded"""

    signature: FileSignature
    """The signature of the file after we downloaded it; if this changed then we
    should double-check the integrity.
    """

    @classmethod
    def from_json(cls, data: dict) -> "ExternalFilesState":
        """Creates an ExternalFilesState from a JSON object"""
        return cls(
            relpath=data["relpath"],
            integrity=data["integrity"],
            signature=FileSignature.from_json(data["signature"]),
        )


@dataclass
class ExternalFilesState:
    """The state of all external files within a build context"""

    state_by_relpath: Dict[str, ExternalFileState]
    """A lookup from the relative path to the external file to its state
    """

    @classmethod
    def from_json(cls, data: dict) -> "ExternalFilesState":
        """Loads the typed object described in the given json object"""
        return ExternalFilesState(
            state_by_relpath=dict(
                (key, ExternalFileState.from_json(value))
                for key, value in data["state_by_relpath"].items()
            )
        )


@dataclass
class JSConstants:
    """The javascript constants to export"""

    relpath: str
    """The path to the constants file relative to the project root. If
    this file does not exist, the constants file will not be produced.
    The contents of this file are ignored, but it's recommended that the
    constants be documented here.
    """

    shared: Dict[str, Union[str, int, float]]
    """The constants which are shared between modes. If a key is both in a shared
    dict and a particular mode, the value from the particular mode will be used.
    """

    dev: Dict[str, Union[str, int, float]]
    """The constants in development mode"""

    prod: Dict[str, Union[str, int, float]]
    """The constants in production mode"""


@dataclass
class BuildContext:
    """Available configuration options when building which may be referenced
    by the file build functionality.
    """

    folder: str
    """The root folder of the project"""

    dev: bool
    """True if we're building for dev watch, false otherwise"""

    symlinks: bool
    """True if symlinks should be used when building, false otherwise"""

    host: Optional[str] = None
    """The host where the website will be deployed, e.g., example.com, if known."""

    default_css_file: str = "src/public/css/main.css"
    """The default css file for imports if not specified"""

    icon_settings: "IconSettings" = None
    """The icon settings to use when generating icons"""

    image_settings: "ImageSettings" = None
    """The image settings to use when generating images"""

    auto_generate_images_js_placeholders: bool = True
    """If true we will generate src folder placeholder *.images.js files"""

    external_files: Dict[str, ExternalFile] = None
    """What external files are required for this project."""

    js_constants: JSConstants = None
    """The javascript constants based on the current build environment"""

    delay_files: List[str] = None
    """Files which, for debugging reasons, we should ensure processing lasts
    at least a few seconds.
    """

    @property
    def src_folder(self) -> str:
        """Returns the src folder where the input files are located"""
        return os.path.join(self.folder, "src")

    @property
    def public_folder(self) -> str:
        """Returns the public folder where publicly accessible files are located"""
        return os.path.join(self.src_folder, "public")

    @property
    def out_folder(self) -> str:
        """Returns the out folder, where easily recreatable files are located"""
        return os.path.join(self.folder, "out")

    @property
    def artifacts_folder(self) -> str:
        """Returns the artifacts folder, where expensive to recreate files are
        located
        """
        return os.path.join(self.folder, "artifacts")

    @property
    def config_file(self) -> str:
        """Returns the path to the config file"""
        return os.path.join(self.folder, "vanillaplusjs.json")

    @property
    def dependency_graph_file(self) -> str:
        """Returns the path to the dependency graph file.
        In this graph, all the files in the graph are input files, and input
        file a is a parent of input file b if the outputs of a depend on b. All
        files are specified relative to the root folder with no leading slash;
        e.g., "src/public/index.html".
        """
        return os.path.join(self.out_folder, "dependency_graph.json")

    @property
    def output_graph_file(self) -> str:
        """Returns the path to the output graph file.
        In this graph, the root files are all input files, but all children are
        either in out/ or in artifacts/. Furthermore, the maximum depth of this
        graph is 1. An input file a is a parent of output file b if output file
        b would be produced exactly as is, so long as a is not modified. Note
        that a single output file may have multiple input files: for example, an
        image which is used in multiple places.
        """
        return os.path.join(self.out_folder, "output_graph.json")

    @property
    def external_files_state_file(self) -> str:
        """Returns the path to the external files state JSON file"""
        return os.path.join(self.out_folder, "external_files_state.json")


def load_external_files(data: Dict[str, Dict]) -> Dict[str, ExternalFile]:
    """Loads the external files from the given data"""
    result = dict()
    for key, value in data.items():
        relpath = value.get("relpath", key).replace("/", os.path.sep)
        result[relpath] = ExternalFile(
            relpath=relpath,
            url=value["url"],
            integrity=value["integrity"],
        )
    return result


def load_js_constants(data: dict) -> JSConstants:
    """Loads the js constants from the given data"""
    return JSConstants(
        relpath=data["relpath"].replace("/", os.path.sep),
        shared=data["shared"],
        dev=data["dev"],
        prod=data["prod"],
    )
