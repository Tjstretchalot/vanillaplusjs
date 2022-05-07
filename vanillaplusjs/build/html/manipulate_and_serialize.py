from typing import List, Optional
from .manipulator import HTMLManipulator
from .builder import HTMLBuilder
import html5lib
import os


def manipulate_and_serialize(
    infile: str, outfile: Optional[str], manipulators: List[HTMLManipulator]
) -> None:
    """Tokenizes the given HTML file, applies the given manipulators to it,
    and writes the resulting tokens to the given file. If the outfile is None,
    this will not output anything, but will still tokenize the file and send
    it to the manipulators as if it were going to, which is useful if the
    manipulators have side-effects.
    """
    builder = HTMLBuilder(manipulators)

    with open(infile, "r") as f:
        tb = html5lib.treebuilders.getTreeBuilder("dom")
        parser = html5lib.HTMLParser(tb, strict=False, namespaceHTMLElements=False)
        try:
            doc = parser.parse(f, scripting=False)
        except html5lib.html5parser.ParseError:
            raise ValueError(
                f"{infile} is not a valid HTML file; errors={parser.errors}"
            )

        walker = html5lib.getTreeWalker("dom")
        for token in walker(doc):
            builder.handle_token(token)

    if outfile is None:
        return

    os.makedirs(os.path.dirname(outfile), exist_ok=True)

    output_tokens = builder.consume_tokens()
    serializer = html5lib.serializer.HTMLSerializer(
        omit_optional_tags=False, quote_attr_values="always"
    )

    with open(outfile, "wb") as f:
        for block in serializer.serialize(output_tokens, encoding="utf-8"):
            f.write(block)
        f.write(bytes(os.linesep, encoding="utf-8"))
