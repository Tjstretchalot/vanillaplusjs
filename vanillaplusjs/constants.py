import os

CONFIGURATION_VERSION = "1.0.0"
"""The configuration version for vanillaplusjs.json, so that we can
automatically migrate old configuration files.
"""

PROCESSOR_VERSION = "1"
"""The version of vanillaplusjs we're using"""


with open(os.path.abspath(os.path.join(__file__, "../../setup.cfg")), "r") as f:
    for line in f:
        line: str
        if line.startswith("version = "):
            PROCESSOR_VERSION = line.split("=")[1].strip()
