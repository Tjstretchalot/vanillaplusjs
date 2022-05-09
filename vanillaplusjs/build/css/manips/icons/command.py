from dataclasses import dataclass
from typing import List, Literal, Optional, Union
from .settings import ButtonSettings
import os


@dataclass
class IconCommand:
    """Describes a parsed preprocessor icon command, before it is augmented with
    the actual color values.
    """

    icon_name: str
    """The identifier for the icon."""

    icon_initial_color: str
    """The color of the icon that is provided as an SVG"""

    output_colors: Optional[List[str]]
    """The colors to output for the icon. None for all available
    colors.
    """

    output_sizes: Optional[List[str]]
    """The sizes to output for the icon. None for all available
    sizes.
    """

    button: Optional[Union[Literal["default"], ButtonSettings]]
    """The button settings for the icon, or the literal `"default"` for
    the default button settings, or `None` for no button
    """

    @property
    def input_icon(self) -> str:
        """The location of the input icon relative to the project root"""
        return os.path.join("src", "public", "img", "icons", self.icon_name + ".svg")

    @property
    def output_icon_folder(self) -> str:
        """The location of the output icon folder relative to the project root"""
        return os.path.join("out", "www", "img", "icons", self.icon_name)

    def web_path_to(self, color: str) -> str:
        """Returns the path part of the URL for this icon in the given color"""
        return f"/img/icons/{self.icon_name}/{color}.svg"
