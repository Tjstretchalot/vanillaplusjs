import helper  # noqa
import unittest
import os
import shutil
import vanillaplusjs.runners.init
import vanillaplusjs.runners.build
import time


class Test(unittest.TestCase):
    def test_copies_html(self):
        os.makedirs(os.path.join("tmp"), exist_ok=True)
        try:
            vanillaplusjs.runners.init.main(["--folder", "tmp"])
            with open(os.path.join("tmp", "src", "public", "index.html"), "w") as f:
                print("<html></html>", file=f)
            vanillaplusjs.runners.build.main(["--folder", "tmp"])
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

    def test_incremental_rebuild_does_not_change_mtime(self):
        os.makedirs(os.path.join("tmp"), exist_ok=True)
        try:
            vanillaplusjs.runners.init.main(["--folder", "tmp"])
            with open(os.path.join("tmp", "src", "public", "index.html"), "w") as f:
                print("<html></html>", file=f)
            vanillaplusjs.runners.build.main(["--folder", "tmp"])
            expected_path = os.path.join("tmp", "out", "www", "index.html")
            # move the mstat to a time far enough in the past that we won't race
            a_bit_ago = time.time() - 100

            try:
                os.utime(expected_path, (a_bit_ago, a_bit_ago), follow_symlinks=False)
            except NotImplementedError:
                os.utime(expected_path, (a_bit_ago, a_bit_ago))

            old_stat = os.lstat(expected_path)
            old_mtime = old_stat.st_mtime
            self.assertAlmostEqual(a_bit_ago, old_mtime, delta=3)  # rounding errors

            vanillaplusjs.runners.build.main(["--folder", "tmp"])

            new_stat = os.lstat(expected_path)
            new_mtime = new_stat.st_mtime
            self.assertEqual(old_mtime, new_mtime)
        finally:
            shutil.rmtree("tmp")

    def test_changed_html_detected(self):
        os.makedirs(os.path.join("tmp"), exist_ok=True)
        infile = os.path.join("tmp", "src", "public", "index.html")
        outfile = os.path.join("tmp", "out", "www", "index.html")
        try:
            vanillaplusjs.runners.init.main(["--folder", "tmp"])
            with open(infile, "w") as f:
                print("<html></html>", file=f)
            vanillaplusjs.runners.build.main(["--folder", "tmp"])
            self.assertTrue(os.path.exists(outfile))

            with open(infile, "r") as f_expected:
                with open(outfile, "r") as f_actual:
                    self.assertEqual(f_expected.read(), f_actual.read())

            with open(infile, "w") as f:
                print("<html><head></head></html>", file=f)

            vanillaplusjs.runners.build.main(["--folder", "tmp"])

            with open(infile, "r") as f_expected:
                with open(outfile, "r") as f_actual:
                    self.assertEqual(f_expected.read(), f_actual.read())
        finally:
            shutil.rmtree("tmp")


if __name__ == "__main__":
    unittest.main()
