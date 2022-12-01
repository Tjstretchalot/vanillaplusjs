from typing import Dict
import helper  # noqa
import unittest
import os
import shutil
import vanillaplusjs.runners.init
import vanillaplusjs.runners.build


# We define these here to avoid breaking the indent flow too much while
# using the """ syntax.
BASIC = {
    "orig": {
        "src/public/js/example.js": "/test/",
        "src/public/js/example2.js": "/\\d/",
        "src/public/js/example3.js": "/\\//",
        "src/public/js/example4.js": "/\\d/g 'foo'",
        "src/public/js/example5.js": "/\\x01/",
        # https://stackoverflow.com/a/46181
        "src/public/js/example6.js": r"/^(([^<>()[\]\.,;:\s@\"]+(\.[^<>()[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$/i",
    },
    "conv": {
        "out/www/js/example.js": "/test/",
        "out/www/js/example2.js": "/\\d/",
        "out/www/js/example3.js": "/\\//",
        "out/www/js/example4.js": '/\\d/g "foo"',
        "out/www/js/example5.js": "/\\x01/",
        "out/www/js/example6.js": r"/^(([^<>()[\]\.,;:\s@\"]+(\.[^<>()[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$/i",
    },
}


class Test(unittest.TestCase):
    def _basic_test(self, orig: Dict[str, str], conv: Dict[str, str]):
        self.maxDiff = None
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

    def test_basic(self):
        self._basic_test(BASIC["orig"], BASIC["conv"])
