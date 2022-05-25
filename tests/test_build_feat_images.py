import dataclasses
from typing import Dict
import helper  # noqa
import unittest
import os
import shutil
from vanillaplusjs.build.file_signature import get_file_signature
import vanillaplusjs.runners.init
import vanillaplusjs.runners.build
import json
from pathlib import Path
from PIL import Image


# We define these here to avoid breaking the indent flow too much while
# using the """ syntax.
BASIC = {
    "orig": {
        "src/public/index.html": """
<!DOCTYPE html>
<html>
<head>
    <title>Test</title>
</head>
<body>
    <!--[IMAGE: /img/test.jpg 20 20]-->
</body>
</html>
"""
    },
    "conv": {
        "out/www/index.html": """<!DOCTYPE html><html><head><meta charset="utf-8">
    <title>Test</title>
</head>
<body>
    <picture><source srcset="/img/test/1/20x20.webp 20w, /img/test/1/30x30.webp 30w"><img width="20" height="20" src="/img/test/1/20x20.jpeg" srcset="/img/test/1/20x20.jpeg 20w, /img/test/1/30x30.jpeg 30w" loading="lazy"></picture>


</body></html>
""",
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

            yield
        finally:
            shutil.rmtree("tmp")

    def test_basic(self):
        os.makedirs(os.path.join("tmp", "src", "public", "img"))
        img = Image.new("RGB", (30, 30), color=(255, 0, 0))
        img.save(os.path.join("tmp", "src", "public", "img", "test.jpg"))

        gen = self._basic_test(BASIC["orig"], BASIC["conv"])
        next(gen)
        try:
            with open("tmp/artifacts/img/test/1/metadata.json", "r") as f:
                meta = json.load(f)
            self.assertIsInstance(meta, dict)
            self.assertIsInstance(meta.get("settings_hash"), int)
            self.assertIsInstance(meta.get("source"), dict)
            self.assertEqual(
                meta["source"].get("path"),
                os.path.join("src", "public", "img", "test.jpg"),
            )
            self.assertEqual(meta["source"].get("width"), 30)
            self.assertEqual(meta["source"].get("height"), 30)
            sign = get_file_signature(
                os.path.join("tmp", "src", "public", "img", "test.jpg")
            )
            self.assertEqual(meta["source"].get("signature"), dataclasses.asdict(sign))

            self.assertIsInstance(meta.get("target"), dict)

            target: dict = meta["target"]
            self.assertIsInstance(target.get("settings"), dict)

            settings: dict = target["settings"]
            self.assertEqual(settings.get("width"), 20)
            self.assertEqual(settings.get("height"), 20)
            self.assertEqual(settings.get("crop"), "cover")
            self.assertEqual(
                settings.get("crop_settings"),
                {
                    "pre_top_crop": 0,
                    "pre_left_crop": 0,
                    "pre_bottom_crop": 0,
                    "pre_right_crop": 0,
                    "crop_left_percentage": 0.5,
                    "crop_top_percentage": 0.5,
                },
            )

            self.assertIsInstance(target.get("outputs"), dict)

            outputs: dict = target["outputs"]
            self.assertIsInstance(target["outputs"].get("webp"), list)
            self.assertIsInstance(target["outputs"].get("jpeg"), list)
            self.assertEqual(len(outputs), 2)
            for output_list in outputs.values():
                for output in output_list:
                    self.assertIsInstance(output, dict)
                    self.assertIsInstance(output.get("width"), int)
                    self.assertIsInstance(output.get("height"), int)
                    self.assertIsInstance(output.get("relpath"), str)
                    self.assertIsInstance(output.get("choice"), str)
                    self.assertEqual(len(output), 4)

            webp: list = outputs["webp"]
            self.assertEqual(len(webp), 2)
            webp = sorted(webp, key=lambda x: x["width"])
            self.assertEqual(webp[0]["width"], 20)
            self.assertEqual(webp[0]["height"], 20)
            self.assertEqual(
                webp[0]["relpath"], os.path.join("img", "test", "1", "20x20.webp")
            )
            self.assertEqual(webp[0]["choice"], "lossless")
            self.assertEqual(webp[1]["width"], 30)
            self.assertEqual(webp[1]["height"], 30)
            self.assertEqual(
                webp[1]["relpath"], os.path.join("img", "test", "1", "30x30.webp")
            )
            self.assertEqual(webp[1]["choice"], "lossless")

            jpeg: list = outputs["jpeg"]
            self.assertEqual(len(jpeg), 2)
            jpeg = sorted(jpeg, key=lambda x: x["width"])
            self.assertEqual(jpeg[0]["width"], 20)
            self.assertEqual(jpeg[0]["height"], 20)
            self.assertEqual(
                jpeg[0]["relpath"], os.path.join("img", "test", "1", "20x20.jpeg")
            )
            self.assertEqual(jpeg[0]["choice"], "100")
            self.assertEqual(jpeg[1]["width"], 30)
            self.assertEqual(jpeg[1]["height"], 30)
            self.assertEqual(
                jpeg[1]["relpath"], os.path.join("img", "test", "1", "30x30.jpeg")
            )
            self.assertEqual(jpeg[1]["choice"], "100")
        finally:
            self.assertRaises(StopIteration, next, gen)

    def test_rebuild_no_error(self):
        os.makedirs(os.path.join("tmp", "src", "public", "img"))
        img = Image.new("RGB", (30, 30), color=(255, 0, 0))
        img.save(os.path.join("tmp", "src", "public", "img", "test.jpg"))
        for _ in self._basic_test(BASIC["orig"], BASIC["conv"]):
            Path(os.path.join("tmp", "src", "public", "index.html")).touch()
            vanillaplusjs.runners.build.main(["--folder", "tmp"])
            Path(os.path.join("tmp", "src", "public", "index.html")).touch()
            vanillaplusjs.runners.build.main(["--folder", "tmp"])
            Path(os.path.join("tmp", "src", "public", "index.html")).touch()
            vanillaplusjs.runners.build.main(["--folder", "tmp"])
