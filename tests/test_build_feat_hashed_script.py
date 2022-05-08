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
        "src/public/js/index.js": "/* we don't need a real script here for this test */",
        "src/public/index.html": """
<!DOCTYPE html>
<html>
<head>
    <title>Test</title>
</head>
<body>
    <div class="bg-white">White background</div>
    <script src="/js/index.js" type="module"></script>
</body>
</html>
""",
    },
    "conv": {
        "out/www/js/index.js": "/* we don't need a real script here for this test */",
        "out/www/index.html": """<!DOCTYPE html><html><head><meta charset="utf-8">
    <title>Test</title>
</head>
<body>
    <div class="bg-white">White background</div>
    <script src="/js/index.js?v=miPr_dZeaCM4PeNb2iCfcKwSMOI5twWfEsyxMep1Pqc=&amp;pv={PROCESSOR_VERSION}" type="module"></script>


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
