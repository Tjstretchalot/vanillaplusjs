import dataclasses
from typing import Dict
import helper  # noqa
import unittest
import os
import shutil
from vanillaplusjs.build.file_signature import get_file_signature
from vanillaplusjs.build.handlers.hash import calculate_hash
import vanillaplusjs.runners.init
import vanillaplusjs.runners.build
import json
from PIL import Image


# We define these here to avoid breaking the indent flow too much while
# using the """ syntax.
BASIC = {
    "orig": {
        "src/public/js/admin.images.json": json.dumps(
            {
                "img1": {
                    "path": "/img/test.jpg",
                    "width": 20,
                    "height": 20,
                    "crop_style": "cover",
                    "crop_arguments": {},
                    "lazy": True,
                }
            }
        )
    },
    "conv": {
        "src/public/js/admin.images.js": True,
        "out/www/js/admin.images.js": True,
        "out/www/js/admin.images.json": False,
        "out/www/js/admin.images.js.hash": "9sXRSdXTD_vsFqf1FHJrYc-okBJHXhMNzH1Cisu5A2g=",
        "out/www/img/test/1/20x20.jpeg": True,
        "out/www/img/test/1/20x20.webp": True,
        "out/www/img/test/1/30x30.jpeg": True,
        "out/www/img/test/1/30x30.webp": True,
        "artifacts/img/test/1/20x20.jpeg": True,
        "artifacts/img/test/1/20x20.webp": True,
        "artifacts/img/test/1/30x30.jpeg": True,
        "artifacts/img/test/1/30x30.webp": True,
        "artifacts/img/test/1/metadata.json": True,
        "artifacts/img/test/counter.txt": "1",
    },
}

WITH_IMAGE_JS_IMPORTED = {
    "orig": {
        "src/public/js/admin.images.json": json.dumps(
            {
                "img1": {
                    "path": "/img/test.jpg",
                    "width": 30,
                    "height": 30,
                    "crop_style": "cover",
                    "crop_arguments": {},
                    "lazy": True,
                }
            }
        ),
        "src/public/js/admin.js": "import adminImages from '/js/admin.images.js';",
    },
    "conv": {
        "src/public/js/admin.images.js": True,
        "out/www/js/admin.images.js": True,
        "out/www/js/admin.images.json": False,
        "out/www/js/admin.images.js.hash": "ZzpI2gkRFCAFbi9LxdLqPGAvzrrKdnwuPvTcBx0uiE8=",
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
                if path.endswith(".hash"):
                    src_path = path[:-5]
                    correct_hash = calculate_hash(os.path.join("tmp", src_path))
                    with open(os.path.join("tmp", path), "r") as f:
                        self.assertEqual(f.read(), correct_hash, path)

                if isinstance(val, str):
                    with open(os.path.join("tmp", path), "r") as f:
                        self.assertEqual(f.read(), val, path)
                elif isinstance(val, bytes):
                    with open(os.path.join("tmp", path), "rb") as f:
                        self.assertEqual(f.read(), val, path)
                elif val is True:
                    self.assertTrue(os.path.lexists(os.path.join("tmp", path)), path)
                elif val is False:
                    self.assertFalse(os.path.lexists(os.path.join("tmp", path)), path)
                else:
                    raise TypeError(f"Unknown type: {type(val)} for {path}")
        finally:
            shutil.rmtree("tmp")

    def test_basic(self):
        os.makedirs(os.path.join("tmp", "src", "public", "img"))
        img = Image.new("RGB", (30, 30), color=(255, 0, 0))
        img.save(os.path.join("tmp", "src", "public", "img", "test.jpg"))

        self._basic_test(BASIC["orig"], BASIC["conv"])

    def test_with_image_js_imported(self):
        os.makedirs(os.path.join("tmp", "src", "public", "img"))
        img = Image.new("RGB", (30, 30), color=(255, 0, 0))
        img.save(os.path.join("tmp", "src", "public", "img", "test.jpg"))

        self._basic_test(WITH_IMAGE_JS_IMPORTED["orig"], WITH_IMAGE_JS_IMPORTED["conv"])
