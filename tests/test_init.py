import helper  # noqa
import unittest
import os
import shutil
import vanillaplusjs.runners.init
import vanillaplusjs.constants
import json


class Test(unittest.TestCase):
    def test_initializes_configuration(self):
        os.makedirs(os.path.join("tmp"), exist_ok=True)
        try:
            vanillaplusjs.runners.init.main(["--folder", "tmp"])
            self.assertTrue(os.path.exists(os.path.join("tmp", "vanillaplusjs.json")))
        finally:
            shutil.rmtree("tmp")

    def test_initializes_configuration_version(self):
        os.makedirs(os.path.join("tmp"), exist_ok=True)
        try:
            vanillaplusjs.runners.init.main(["--folder", "tmp"])
            with open(os.path.join("tmp", "vanillaplusjs.json")) as f:
                configuration = json.load(f)

            self.assertEqual(configuration["version"], vanillaplusjs.constants.CONFIGURATION_VERSION)
        finally:
            shutil.rmtree("tmp")

    def test_initializes_folders(self):
        os.makedirs(os.path.join("tmp"), exist_ok=True)
        try:
            vanillaplusjs.runners.init.main(["--folder", "tmp"])
            self.assertTrue(os.path.exists(os.path.join("tmp", "src", "public", "img")))
            self.assertTrue(os.path.exists(os.path.join("tmp", "src", "public", "js")))
            self.assertTrue(
                os.path.exists(os.path.join("tmp", "src", "public", "partials"))
            )
        finally:
            shutil.rmtree("tmp")


if __name__ == "__main__":
    unittest.main()
