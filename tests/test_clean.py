import helper  # noqa
import unittest
import os
import shutil
import vanillaplusjs.runners.init
import vanillaplusjs.runners.build
import vanillaplusjs.runners.clean


class Test(unittest.TestCase):
    def test_removes_out(self):
        os.makedirs(os.path.join("tmp"), exist_ok=True)
        try:
            vanillaplusjs.runners.init.main(["--folder", "tmp"])
            vanillaplusjs.runners.build.main(["--folder", "tmp"])
            self.assertTrue(
                os.path.exists(os.path.join("tmp", "out", "www", "index.html"))
            )
            vanillaplusjs.runners.clean.main(["--folder", "tmp"])
            self.assertFalse(
                os.path.exists(os.path.join("tmp", "out", "www", "index.html"))
            )
        finally:
            shutil.rmtree("tmp")


if __name__ == "__main__":
    unittest.main()
