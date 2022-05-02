import helper  # noqa
import unittest
import os
import shutil
import vanillaplusjs.runners.init
import vanillaplusjs.runners.build


class Test(unittest.TestCase):
    def test_copies_html(self):
        os.makedirs(os.path.join("tmp"), exist_ok=True)
        try:
            vanillaplusjs.runners.init.main(["--folder", "tmp"])
            with open(os.path.join("tmp", "src", "public", "index.html"), "w") as f:
                print("<html></html>", file=f)
            vanillaplusjs.runners.build.main(
                ["--infolder", "tmp", "--outfolder", "tmp/out"]
            )
            self.assertTrue(
                os.path.exists(os.path.join("tmp", "out", "www", "index.html"))
            )

            with open(
                os.path.join("tmp", "src", "public", "index.html"), "r"
            ) as f_expected:
                with open(
                    os.path.join("tmp", "out", "www", "index.html"), "r"
                ) as f_actual:
                    self.assertEqual(f_expected.read(), f_actual.read())
        finally:
            shutil.rmtree("tmp")


if __name__ == "__main__":
    unittest.main()
