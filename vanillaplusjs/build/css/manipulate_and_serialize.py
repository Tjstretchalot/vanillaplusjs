from typing import List, Optional
from .manipulator import CSSManipulator
from .builder import CSSBuilder
from .tokenizer import tokenize
from .serializer import serialize
import os


def manipulate_and_serialize(
    infile: str, outfile: Optional[str], manipulators: List[CSSManipulator]
) -> None:
    """Tokenizes the given CSS file, applies the given manipulators to it,
    and writes the resulting tokens to the given file. If the outfile is None,
    this will not output anything, but will still tokenize the file and send
    it to the manipulators as if it were going to, which is useful if the
    manipulators have side-effects.
    """
    builder = CSSBuilder(manipulators)

    if outfile is None:
        with open(infile, "r") as f:
            for token in tokenize(f):
                builder.handle_token(token)
        return

    out_dir = os.path.dirname(outfile)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(infile, "r") as f_in:
        with open(outfile, "w") as f_out:
            for in_token in tokenize(f_in):
                builder.handle_token(in_token)
                for out_token in builder.consume_tokens():
                    f_out.write(serialize(out_token))
