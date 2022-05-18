import helper  # noqa
import unittest
import os
import shutil
from vanillaplusjs.build.file_signature import get_file_signature
import vanillaplusjs.runners.init
import vanillaplusjs.runners.build
import json
import hashlib
from base64 import b64encode


def get_sha384(filepath: str) -> str:
    digest = hashlib.sha384()
    with open(filepath, "rb") as f_in:
        while True:
            data = f_in.read(4096)
            if not data:
                break
            digest.update(data)

    return str(b64encode(digest.digest()), "ascii")


class Test(unittest.TestCase):
    def test_downloads_bootstrap(self):
        os.makedirs(os.path.join("tmp"), exist_ok=True)
        try:
            vanillaplusjs.runners.init.main(["--folder", "tmp"])
            with open("tmp/vanillaplusjs.json", "r") as f:
                old_config = json.load(f)

            old_config["external_files"] = {
                "src/public/css/lib/bootstrap.min.css": {
                    "url": "https://cdn.jsdelivr.net/npm/bootstrap@5.2.0-beta1/dist/css/bootstrap.min.css",
                    "integrity": "sha384-0evHe/X+R7YkIZDRvuzKMRqM+OrBnVFBL6DOitfPri4tjfHxaWutUpFmBp4vmVor",
                },
                "src/public/js/lib/bootstrap.min.js": {
                    "url": "https://cdn.jsdelivr.net/npm/bootstrap@5.2.0-beta1/dist/js/bootstrap.bundle.min.js",
                    "integrity": "sha384-pprn3073KE6tl6bjs2QrFaJGz5/SUsLqktiwsUTF55Jfv3qYSDhgCecCxMW52nD2",
                },
            }

            with open("tmp/vanillaplusjs.json", "w") as f:
                json.dump(old_config, f, indent=2)

            vanillaplusjs.runners.build.main(["--folder", "tmp"])
            self.assertEqual(
                get_sha384(
                    os.path.join(
                        "tmp", "src", "public", "css", "lib", "bootstrap.min.css"
                    )
                ),
                "0evHe/X+R7YkIZDRvuzKMRqM+OrBnVFBL6DOitfPri4tjfHxaWutUpFmBp4vmVor",
            )
            self.assertEqual(
                get_sha384(
                    os.path.join(
                        "tmp", "src", "public", "js", "lib", "bootstrap.min.js"
                    )
                ),
                "pprn3073KE6tl6bjs2QrFaJGz5/SUsLqktiwsUTF55Jfv3qYSDhgCecCxMW52nD2",
            )

            # from here forth should be a different test but processing bootstrap
            # is slow so we don't want to do it twice

            old_src_sig = get_file_signature(
                os.path.join("tmp", "src", "public", "css", "lib", "bootstrap.min.css")
            )
            old_out_sig = get_file_signature(
                os.path.join("tmp", "out", "www", "css", "lib", "bootstrap.min.css")
            )

            vanillaplusjs.runners.build.main(["--folder", "tmp"])

            self.assertEqual(
                old_src_sig,
                get_file_signature(
                    os.path.join(
                        "tmp", "src", "public", "css", "lib", "bootstrap.min.css"
                    )
                ),
                "shouldn't need to redownload",
            )

            self.assertEqual(
                old_out_sig,
                get_file_signature(
                    os.path.join("tmp", "out", "www", "css", "lib", "bootstrap.min.css")
                ),
                "shouldn't need to reprocess",
            )
        finally:
            shutil.rmtree("tmp")


if __name__ == "__main__":
    unittest.main()
