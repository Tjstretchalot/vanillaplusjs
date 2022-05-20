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
        "src/public/index.html": """
<!DOCTYPE html>
<html>
<head>
    <meta property="og:url">
    <title>Home</title>
</head>
<body>
    <div class="bg-white">White background</div>
</body>
</html>
""",
    },
    "conv": {
        "out/www/index.html": """<!DOCTYPE html><html><head><meta charset="utf-8">
    <meta content="https://example.com/index.html" property="og:url">
    <title>Home</title>
</head>
<body>
    <div class="bg-white">White background</div>


</body></html>
""",
    },
}


OVERRIDE_EMPTY = {
    "orig": {
        "src/public/index.html": """
<!DOCTYPE html>
<html>
<head>
    <meta content="" property="og:url">
    <title>Home</title>
</head>
<body>
    <div class="bg-white">White background</div>
</body>
</html>
""",
    },
    "conv": {
        "out/www/index.html": """<!DOCTYPE html><html><head><meta charset="utf-8">
    <meta content="https://example.com" property="og:url">
    <title>Home</title>
</head>
<body>
    <div class="bg-white">White background</div>


</body></html>
""",
    },
}


OVERRIDE_SLASH = {
    "orig": {
        "src/public/index.html": """
<!DOCTYPE html>
<html>
<head>
    <meta content="/" property="og:url">
    <title>Home</title>
</head>
<body>
    <div class="bg-white">White background</div>
</body>
</html>
""",
    },
    "conv": {
        "out/www/index.html": """<!DOCTYPE html><html><head><meta charset="utf-8">
    <meta content="https://example.com/" property="og:url">
    <title>Home</title>
</head>
<body>
    <div class="bg-white">White background</div>


</body></html>
""",
    },
}


OVERRIDE_PATH = {
    "orig": {
        "src/public/index.html": """
<!DOCTYPE html>
<html>
<head>
    <meta content="/try" property="og:url">
    <title>Home</title>
</head>
<body>
    <div class="bg-white">White background</div>
</body>
</html>
""",
    },
    "conv": {
        "out/www/index.html": """<!DOCTYPE html><html><head><meta charset="utf-8">
    <meta content="https://example.com/try" property="og:url">
    <title>Home</title>
</head>
<body>
    <div class="bg-white">White background</div>


</body></html>
""",
    },
}


class Test(unittest.TestCase):
    def _basic_test(self, orig: Dict[str, str], conv: Dict[str, str]):
        os.makedirs(os.path.join("tmp"), exist_ok=True)
        try:
            vanillaplusjs.runners.init.main(
                ["--folder", "tmp", "--host", "example.com"]
            )
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

    def test_override_empty(self):
        self._basic_test(OVERRIDE_EMPTY["orig"], OVERRIDE_EMPTY["conv"])

    def test_override_slash(self):
        self._basic_test(OVERRIDE_SLASH["orig"], OVERRIDE_SLASH["conv"])

    def test_override_path(self):
        self._basic_test(OVERRIDE_PATH["orig"], OVERRIDE_PATH["conv"])
