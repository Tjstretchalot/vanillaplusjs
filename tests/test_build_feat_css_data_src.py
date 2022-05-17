from typing import Dict
import helper  # noqa
import unittest
import os
import shutil
from vanillaplusjs.constants import PROCESSOR_VERSION
import vanillaplusjs.runners.init
import vanillaplusjs.runners.build


# We define these here to avoid breaking the indent flow too much while
# using the """ syntax.
BASIC = {
    "orig": {
        "src/public/css/main.css": """
.button {
    background: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3e%3cpath fill='none' stroke='%23343a40' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M2 5l6 6 6-6'/%3e%3c/svg%3e");
}
""",
    },
    "conv": {
        "out/www/img/gen/css/main/1.svg": "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'><path fill='none' stroke='#343a40' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M2 5l6 6 6-6'/></svg>",
        "out/www/img/gen/css/main/1.svg.hash": "gprT7QwviS59-EmJB43UJG_ApfGheUOeYxRGJGXbsvY=",
        "out/www/css/main.css": """
.button {
    background: url("/img/gen/css/main/1.svg?v=gprT7QwviS59-EmJB43UJG_ApfGheUOeYxRGJGXbsvY=&pv={PROCESSOR_VERSION}");
}
""".replace(
            "{PROCESSOR_VERSION}", PROCESSOR_VERSION
        ),
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
