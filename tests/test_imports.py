"""Very sophisticated test which just imports everything.
"""
import unittest
import os
import helper  # noqa
from importlib import import_module


class Test(unittest.TestCase):
    def test_import_all(self):
        for rootp, _, files in os.walk("src"):
            for f in files:
                if not f.endswith(".py"):
                    continue
                fullpath = os.path.join(rootp, f)
                modpath = fullpath[4:-3].replace(os.path.sep, ".")
                try:
                    import_module(modpath)
                except:
                    print(f"While trying {fullpath} via {modpath}")
                    raise


if __name__ == "__main__":
    unittest.main()
