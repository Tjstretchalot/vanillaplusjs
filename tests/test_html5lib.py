import unittest
import html5lib
import os


SAMPLE_HTML = (
    '<!DOCTYPE html><html><head><meta charset="utf-8"></head><body></body></html>'
)
"""The html which will be faithfully replicated by html5lib. Notice that if you
add suffixed whitespace, it will be moved into the body. This can be annoying
in tests.
"""


class Test(unittest.TestCase):
    def test_copies_faithfully(self):
        doc = html5lib.parse(SAMPLE_HTML, treebuilder="dom")
        walker = html5lib.getTreeWalker("dom")
        serializer = html5lib.serializer.HTMLSerializer(
            quote_attr_values="always", omit_optional_tags=False
        )
        output = serializer.render(walker(doc), encoding="utf-8")
        self.assertEqual(bytes(SAMPLE_HTML, "utf-8"), output)

    def test_serialize_copies_faithfully(self):
        doc = html5lib.parse(SAMPLE_HTML, treebuilder="dom")
        walker = html5lib.getTreeWalker("dom")
        serializer = html5lib.serializer.HTMLSerializer(
            quote_attr_values="always",
            omit_optional_tags=False,
        )

        try:
            with open("test.txt", "wb") as f:
                for block in serializer.serialize(walker(doc), encoding="utf-8"):
                    f.write(block)

            with open("test.txt", "r") as f:
                self.assertEqual(SAMPLE_HTML, f.read())
        finally:
            os.remove("test.txt")

    def test_parser_settings_copies_faithfully(self):
        tb = html5lib.treebuilders.getTreeBuilder("dom")
        parser = html5lib.HTMLParser(tb, strict=True, namespaceHTMLElements=False)
        doc = parser.parse(SAMPLE_HTML, scripting=False)
        walker = html5lib.getTreeWalker("dom")
        output_tokens = list(walker(doc))

        serializer = html5lib.serializer.HTMLSerializer(
            omit_optional_tags=False, quote_attr_values="always"
        )

        output = serializer.render(output_tokens, encoding="utf-8")

        self.assertEqual(bytes(SAMPLE_HTML, "utf-8"), output)


if __name__ == "__main__":
    unittest.main()
