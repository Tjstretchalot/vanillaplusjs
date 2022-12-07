from typing import List, Optional

from vanillaplusjs.build.ioutil import makedirs_safely
from .manipulator import HTMLManipulator
from .builder import HTMLBuilder
from .tokenizer import tokenize
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
        try:
            for token in tokenize(f):
                builder.handle_token(token)
        except html5lib.html5parser.ParseError:
            raise ValueError(f"{infile} is not a valid HTML file")

    if outfile is None:
        return

    makedirs_safely(os.path.dirname(outfile))

    output_tokens = builder.consume_tokens()
    serializer = html5lib.serializer.HTMLSerializer(
        omit_optional_tags=False, quote_attr_values="always"
    )

    with open(outfile, "wb") as f:
        for block in serializer.serialize(output_tokens, encoding="utf-8"):
            f.write(block)
        f.write(bytes(os.linesep, encoding="utf-8"))
