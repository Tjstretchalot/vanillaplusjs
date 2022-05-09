from dataclasses import dataclass
import os
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from vanillaplusjs.build.css.manips.icons.settings import IconSettings


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
    def artifacts_Folder(self) -> str:
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
