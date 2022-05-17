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
        "src/public/css/main.css": """
.bg-white {
    background: white;
}
""",
        "src/public/index.html": """
<!DOCTYPE html>
<html>
<head>
    <title>Test</title>
    <link rel="stylesheet" href="/css/main.css">
</head>
<body>
    <div class="bg-white">White background</div>
</body>
</html>
""",
    },
    "conv": {
        "out/www/css/main.css": """
.bg-white {
    background: white;
}
""",
        "out/www/index.html": """<!DOCTYPE html><html><head><meta charset="utf-8">
    <title>Test</title>
    <link href="/css/main.css?v=tgySJ8RxDTfHHxh8YLiT3PluZoOE6QKptkIa5-W2EbY%3D&amp;pv={PROCESSOR_VERSION}" rel="stylesheet">
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
