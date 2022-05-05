from typing import Dict
import helper  # noqa
import unittest
import os
import shutil
from vanillaplusjs.build.exceptions import MissingConfigurationException
import vanillaplusjs.runners.init
import vanillaplusjs.runners.build


# We define these here to avoid breaking the indent flow while
# using the """ syntax.
BASIC_SAME_FILE_ORIG = """
.bg-white {
    background: white;
}

.button {
    padding: 12px;
    /*! PREPROCESSOR: import .bg-white */
}
"""

BASIC_SAME_FILE_CONV = """
.bg-white {
    background: white;
}

.button {
    padding: 12px;
    background: white;
}
"""

INVERTED_SAME_FILE_ORIG = """
.button {
    padding: 12px;
    /*! PREPROCESSOR: import .bg-white */
}

.bg-white {
    background: white;
}
"""

INVERTED_SAME_FILE_CONV = """
.button {
    padding: 12px;
    background: white;
}

.bg-white {
    background: white;
}
"""

INVERTED_DEEP_ORIG = """
.button {
    padding: 12px;
    /*! PREPROCESSOR: import .elevated-small */
}

.elevated-small {
    /*! PREPROCESSOR: import .bg-white */
    /*! PREPROCESSOR: import .box-shadow-small */
}

.bg-white {
    background: white;
}

.box-shadow-small {
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
}
"""

INVERTED_DEEP_CONV = """
.button {
    padding: 12px;
    background: white;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
}

.elevated-small {
    background: white;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
}

.bg-white {
    background: white;
}

.box-shadow-small {
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
}
"""

MULTI_A_ORIG = """
.bg-white {
    background: white;
}
"""

MULTI_A_CONV = MULTI_A_ORIG

MULTI_B_ORIG = """
.button {
    /*! PREPROCESSOR: import .bg-white FROM /css/a.css */
}
"""

MULTI_B_CONV = """
.button {
    background: white;
}
"""


class Test(unittest.TestCase):
    def _basic_test(self, orig: Dict[str, str], conv: Dict[str, str]):
        os.makedirs(os.path.join("tmp"), exist_ok=True)
        try:
            vanillaplusjs.runners.init.main(["--folder", "tmp"])
            for path, val in orig.items():
                os.makedirs(os.path.dirname(os.path.join("tmp", path)), exist_ok=True)
                with open(os.path.join("tmp", path), "w") as f:
                    f.write(val)

            vanillaplusjs.runners.build.main(["--folder", "tmp"])

            for path, val in conv.items():
                with open(os.path.join("tmp", path), "r") as f:
                    self.assertEqual(f.read(), val, path)
        finally:
            shutil.rmtree("tmp")

    def test_basic_same_file(self):
        self._basic_test(
            dict(
                (
                    (
                        os.path.join("src", "public", "css", "main.css"),
                        BASIC_SAME_FILE_ORIG,
                    ),
                )
            ),
            dict(
                (
                    (
                        os.path.join("out", "www", "css", "main.css"),
                        BASIC_SAME_FILE_CONV,
                    ),
                )
            ),
        )

    def test_basic_inverted_same_file(self):
        self._basic_test(
            dict(
                (
                    (
                        os.path.join("src", "public", "css", "main.css"),
                        INVERTED_SAME_FILE_ORIG,
                    ),
                )
            ),
            dict(
                (
                    (
                        os.path.join("out", "www", "css", "main.css"),
                        INVERTED_SAME_FILE_CONV,
                    ),
                )
            ),
        )

    def test_basic_inverted_deep(self):
        self._basic_test(
            dict(
                (
                    (
                        os.path.join("src", "public", "css", "main.css"),
                        INVERTED_DEEP_ORIG,
                    ),
                )
            ),
            dict(
                (
                    (
                        os.path.join("out", "www", "css", "main.css"),
                        INVERTED_DEEP_CONV,
                    ),
                )
            ),
        )

    def test_multi(self):
        self._basic_test(
            dict(
                (
                    (
                        os.path.join("src", "public", "css", "a.css"),
                        MULTI_A_ORIG,
                    ),
                    (
                        os.path.join("src", "public", "css", "b.css"),
                        MULTI_B_ORIG,
                    ),
                )
            ),
            dict(
                (
                    (
                        os.path.join("out", "www", "css", "a.css"),
                        MULTI_A_CONV,
                    ),
                    (
                        os.path.join("out", "www", "css", "b.css"),
                        MULTI_B_CONV,
                    ),
                )
            ),
        )
