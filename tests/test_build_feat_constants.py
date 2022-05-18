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

            old_config["js_constants"] = {
                "relpath": "src/public/js/constants.js",
                "shared": {
                    "SHARED_INT": 5,
                    "SHARED_TRUE": True,
                    "SHARED_FALSE": False,
                    "SHARED_FLOAT": 3.0,
                    "SHARED_STR_1": "hello",
                    "SHARED_STR_2": "with 'single' quotes",
                    "SHARED_STR_3": 'with "double" quotes',
                    "SHARED_STR_4": "with \"double\" and 'single' quotes",
                    "SHARED_STR_5": "with literal \\escape",
                    "MODE": "shared",
                },
                "dev": {"MODE": "dev"},
                "prod": {"MODE": "prod"},
            }

            with open("tmp/vanillaplusjs.json", "w") as f:
                json.dump(old_config, f, indent=2)

            with open("tmp/src/public/js/constants.js", "w") as f:
                pass

            vanillaplusjs.runners.build.main(["--folder", "tmp"])
            with open("tmp/out/www/js/constants.js.hash", "r") as f:
                self.assertEqual(
                    "PyNlZOS8hJtBQEacaeaiPngvDCi006V6zLAPUe1RxMc=", f.read()
                )

            vanillaplusjs.runners.build.main(["--folder", "tmp", "--dev"])
            with open("tmp/out/www/js/constants.js.hash", "r") as f:
                self.assertEqual(
                    "yfxQLH4swtohmdlHBArWsfgDSSO1Jgos5x19k1bbFYg=", f.read()
                )
        finally:
            shutil.rmtree("tmp")


if __name__ == "__main__":
    unittest.main()
