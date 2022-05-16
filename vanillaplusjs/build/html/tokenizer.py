import io
from tkinter import E
from typing import Generator
from .token import HTMLToken
import html5lib


def tokenize(f: io.TextIOBase, fragment=False) -> Generator[HTMLToken, None, None]:
    """Tokenizes the given file using html5lib. This will correct certain
    parsing issues with html5lib, such as it improperly missing the comment
    in the fragment <title><!--comment-->hi</title>

    Args:
        f: The file to tokenize.
        fragment: Whether or not this is a fragment of HTML rather than a
            full document.

    Yields:
        HTMLToken: The tokens in the file.

    Sends:
        None

    Returns:
        None
    """
    tb = html5lib.treebuilders.getTreeBuilder("dom")
    parser = html5lib.HTMLParser(tb, strict=False, namespaceHTMLElements=False)
    if fragment:
        doc = parser.parseFragment(f)
    else:
        doc = parser.parse(f)
    walker = html5lib.getTreeWalker("dom")

    tokens = iter(walker(doc))
    while True:
        try:
            token = next(tokens)
        except StopIteration:
            break

        # html5lib uses parseRCDataRawtext for several locations, e.g.,
        # title tags, where we really just want them handled like a normal tag.
        # it's not really possible to fix this without forking html5lib, so we
        # will at least handle comments correctly

        # to see what we're trying to fix, try parseFragment on <title><!-- COMMENT -->Hello World</title>

        if token["type"] == "Characters" and token["data"] == "<":
            try:
                next_token = next(tokens)
            except StopIteration:
                yield token
                break

            if next_token["type"] == "Characters" and next_token["data"].startswith(
                "!--"
            ):
                data: str = next_token["data"]
                try:
                    close_comment_idx = data.index("-->")
                except ValueError:
                    yield token
                    yield next_token
                    continue

                yield HTMLToken(
                    type="Comment",
                    data=data[3:close_comment_idx],
                )
                remainder = data[close_comment_idx + 3 :]
                if remainder:
                    yield HTMLToken(
                        type="Characters",
                        data=remainder,
                    )
                continue

            yield token
            yield next_token
            continue

        yield token
