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

# We use import syntax in the same order as https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import
EXPECTED_SUFFIX = (
    f"v=miPr_dZeaCM4PeNb2iCfcKwSMOI5twWfEsyxMep1Pqc%3D&pv={PROCESSOR_VERSION}"
)
EXPECTED_IMPORT_PATH_LITERAL = f'"/js/example.js?{EXPECTED_SUFFIX}"'
BASIC = {
    "orig": {
        "src/public/js/example.js": "/* we don't need a real script here for this test */",
        "src/public/js/example2.js": 'import defaultExport from "/js/example.js";',
        "src/public/js/example3.js": 'import * as name from "/js/example.js";',
        "src/public/js/example4.js": 'import { export1 } from "/js/example.js";',
        "src/public/js/example5.js": 'import { export1 as alias1 } from "/js/example.js";',
        "src/public/js/example6.js": 'import { export1, export2 } from "/js/example.js";',
        "src/public/js/example7.js": 'import { export1, export2 as alias2 } from "/js/example.js";',
        "src/public/js/example8.js": 'import defaultExport, { export1 } from "/js/example.js";',
        "src/public/js/example9.js": 'import defaultExport, * as name from "/js/example.js";',
        "src/public/js/example10.js": 'import "/js/example.js";',
    },
    "conv": {
        "out/www/js/example.js": "/* we don't need a real script here for this test */",
        "out/www/js/example2.js": f"import defaultExport from {EXPECTED_IMPORT_PATH_LITERAL};",
        "out/www/js/example3.js": f"import * as name from {EXPECTED_IMPORT_PATH_LITERAL};",
        "out/www/js/example4.js": f"import {{ export1 }} from {EXPECTED_IMPORT_PATH_LITERAL};",
        "out/www/js/example5.js": f"import {{ export1 as alias1 }} from {EXPECTED_IMPORT_PATH_LITERAL};",
        "out/www/js/example6.js": f"import {{ export1, export2 }} from {EXPECTED_IMPORT_PATH_LITERAL};",
        "out/www/js/example7.js": f"import {{ export1, export2 as alias2 }} from {EXPECTED_IMPORT_PATH_LITERAL};",
        "out/www/js/example8.js": f"import defaultExport, {{ export1 }} from {EXPECTED_IMPORT_PATH_LITERAL};",
        "out/www/js/example9.js": f"import defaultExport, * as name from {EXPECTED_IMPORT_PATH_LITERAL};",
        "out/www/js/example10.js": f"import {EXPECTED_IMPORT_PATH_LITERAL};",
    },
}


class Test(unittest.TestCase):
    def _basic_test(self, orig: Dict[str, str], conv: Dict[str, str]):
        os.makedirs(os.path.join("tmp"), exist_ok=True)
        try:
            vanillaplusjs.runners.init.main(["--folder", "tmp"])
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
