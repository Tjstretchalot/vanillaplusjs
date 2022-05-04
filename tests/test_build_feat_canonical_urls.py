import helper  # noqa
import unittest
import os
import shutil
from vanillaplusjs.build.exceptions import MissingConfigurationException
import vanillaplusjs.runners.init
import vanillaplusjs.runners.build


class Test(unittest.TestCase):
    def test_empty_canonical_no_init(self):
        os.makedirs(os.path.join("tmp"), exist_ok=True)
        try:
            vanillaplusjs.runners.init.main(["--folder", "tmp"])
            with open(os.path.join("tmp", "src", "public", "index.html"), "w") as f:
                print(
                    '<!DOCTYPE html><html><head><meta charset="utf-8"><link rel="canonical"></head><body></body></html>',
                    file=f,
                )
            self.assertRaises(
                MissingConfigurationException,
                vanillaplusjs.runners.build.main,
                ["--folder", "tmp"],
            )
        finally:
            shutil.rmtree("tmp")

    def test_empty_canonical_with_init(self):
        os.makedirs(os.path.join("tmp"), exist_ok=True)
        try:
            vanillaplusjs.runners.init.main(
                ["--folder", "tmp", "--host", "example.com"]
            )
            with open(os.path.join("tmp", "src", "public", "index.html"), "w") as f:
                f.write(
                    '<!DOCTYPE html><html><head><meta charset="utf-8"><link rel="canonical"></head><body></body></html>'
                )
            vanillaplusjs.runners.build.main(["--folder", "tmp"])
            with open(os.path.join("tmp", "out", "www", "index.html"), "r") as f:
                self.assertEqual(
                    f.read(),
                    "<!DOCTYPE html><html>"
                    '<head><meta charset="utf-8"><link href="https://example.com/index.html" rel="canonical"></head>'
                    "<body></body></html>\n",
                )
        finally:
            shutil.rmtree("tmp")

    def test_relative_canonical_with_init(self):
        os.makedirs(os.path.join("tmp"), exist_ok=True)
        try:
            vanillaplusjs.runners.init.main(
                ["--folder", "tmp", "--host", "example.com"]
            )
            with open(os.path.join("tmp", "src", "public", "index.html"), "w") as f:
                f.write(
                    '<!DOCTYPE html><html><head><meta charset="utf-8"><link rel="canonical" href="/"></head><body></body></html>'
                )
            vanillaplusjs.runners.build.main(["--folder", "tmp"])
            with open(os.path.join("tmp", "out", "www", "index.html"), "r") as f:
                self.assertEqual(
                    f.read(),
                    "<!DOCTYPE html><html>"
                    '<head><meta charset="utf-8"><link href="https://example.com/" rel="canonical"></head>'
                    "<body></body></html>\n",
                )
        finally:
            shutil.rmtree("tmp")


if __name__ == "__main__":
    unittest.main()
