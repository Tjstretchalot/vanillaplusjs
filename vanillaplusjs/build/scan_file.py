from vanillaplusjs.build.build_context import BuildContext
import vanillaplusjs.build.handlers.copy_and_hash
import vanillaplusjs.build.handlers.html
import vanillaplusjs.build.handlers.css
import vanillaplusjs.build.handlers.js
import vanillaplusjs.build.handlers.js_constants
import vanillaplusjs.build.handlers.image_glue
from vanillaplusjs.build.scan_file_result import ScanFileResult


def scan_file(context: "BuildContext", relpath: str) -> ScanFileResult:
    """Synchronously parses the given file and returns the list of files it
    directly depends on and the files it will produce when built. This should
    not be recursive; it can be assumed that if any of the returned files have
    dependencies, and those dependencies change, then the file will be rebuilt.

    This can generally be faster than actually building the target.

    Args:
        context (BuildContext): The context for the build
        relpath (str): The relative path to the file to scan within the root.
            If the root is '/var/myproj' and relpath is 'src/public/index.html' then
            the file to parse is at `/var/myproj/src/public/index.html`.

    Returns:
        ScanFileResult: What the file depends on and what it will produce
    """
    if relpath == context.js_constants.relpath:
        return vanillaplusjs.build.handlers.js_constants.scan_file(context, relpath)
    if vanillaplusjs.build.handlers.image_glue.handles_file(context, relpath):
        return vanillaplusjs.build.handlers.image_glue.scan_file(context, relpath)
    if relpath.endswith(".html"):
        return vanillaplusjs.build.handlers.html.scan_file(context, relpath)
    elif relpath.endswith(".css"):
        return vanillaplusjs.build.handlers.css.scan_file(context, relpath)
    elif relpath.endswith(".js"):
        return vanillaplusjs.build.handlers.js.scan_file(context, relpath)
    return vanillaplusjs.build.handlers.copy_and_hash.scan_file(context, relpath)
