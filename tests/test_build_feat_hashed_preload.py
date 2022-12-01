from typing import Dict
import helper  # noqa
import unittest
import os
import shutil
import vanillaplusjs.runners.init
import vanillaplusjs.runners.build
from vanillaplusjs.constants import PROCESSOR_VERSION


# We define these here to avoid breaking the indent flow too much while
# using the """ syntax.
BASIC = {
    "orig": {
        "src/public/assets/fonts/test.ttf": "we don't need a real font here for this test",
        "src/public/css/main.css": """
@font-face {
    font-family: "Test";
    src: url("/assets/fonts/test.ttf");
    font-weight: normal;
    font-style: normal;
}
""",
        "src/public/index.html": """
<!DOCTYPE html>
<html>
<head>
    <title>Test</title>
    <link as="font" href="/assets/fonts/test.ttf" rel="preload" type="font/ttf">
</head>
<body>
    <div class="bg-white">White background</div>
</body>
</html>
""",
    },
    "conv": {
        "out/www/assets/fonts/test.ttf": "we don't need a real font here for this test",
        "out/www/css/main.css": """
@font-face {{
    font-family: "Test";
    src: url("/assets/fonts/test.ttf?v=QUVT2uNMmAwpHxaQ4w6wrDdwddIgvIWPbLF0X9wZKjs%3D&pv={PROCESSOR_VERSION}");
    font-weight: normal;
    font-style: normal;
}}
""".format(
            PROCESSOR_VERSION=PROCESSOR_VERSION
        ),
        "out/www/index.html": """<!DOCTYPE html><html><head><meta charset="utf-8">
    <title>Test</title>
    <link as="font" href="/assets/fonts/test.ttf?v=QUVT2uNMmAwpHxaQ4w6wrDdwddIgvIWPbLF0X9wZKjs%3D&amp;pv={PROCESSOR_VERSION}" rel="preload" type="font/ttf">
</head>
<body>
    <div class="bg-white">White background</div>


</body></html>
""".format(
            PROCESSOR_VERSION=PROCESSOR_VERSION
        ),
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
