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
        "src/public/js/example.js": "'foobar' // @@type-hint",
        "src/public/js/example2.js": "const a = 5;\nconst b = 3; // @@type-hint",
        "src/public/js/example3.js": "const a = 5;\nconst b = 3; // @@type-hint\nconst c = 4;",
    },
    "conv": {
        "out/www/js/example.js": '/*"foobar" /* @@type-hint*\/*/',
        "out/www/js/example2.js": "const a = 5;\n/*const b = 3; /* @@type-hint*\/*/",
        "out/www/js/example3.js": "const a = 5;\n/*const b = 3; /* @@type-hint*\/*/\nconst c = 4;",
    },
}


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

    def test_basic(self):
        self._basic_test(BASIC["orig"], BASIC["conv"])
