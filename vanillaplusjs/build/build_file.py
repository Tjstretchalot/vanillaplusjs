from .build_context import BuildContext
from .build_file_result import BuildFileResult
import vanillaplusjs.build.handlers.copy_and_hash
import vanillaplusjs.build.handlers.html
import vanillaplusjs.build.handlers.css
import vanillaplusjs.build.handlers.js
import vanillaplusjs.build.handlers.js_constants
import vanillaplusjs.build.handlers.image_glue


def build_file(build_context: "BuildContext", relpath: str) -> BuildFileResult:
    """Builds the file within the given context. This assumes that all the
    children have already been built. This MUST be multi-process safe; this MAY
    be called concurrently for different files.

    It is guarranteed that we will not concurrently build two files which
    produce the same outputs, unless those outputs have already been built.

    It is guarranteed that if an output will be built by this, if it already
    exists, it can be assumed that it will be the same as the output produced
    by this.

    Args:
        build_context (BuildContext): The configuration for the build

    Returns:
        BuildFileResult: If the file is built successfully
    """
    if relpath == build_context.js_constants.relpath:
        return vanillaplusjs.build.handlers.js_constants.build_file(
            build_context, relpath
        )
    if vanillaplusjs.build.handlers.image_glue.handles_file(build_context, relpath):
        return vanillaplusjs.build.handlers.image_glue.build_file(
            build_context, relpath
        )
    if relpath.endswith(".html"):
        return vanillaplusjs.build.handlers.html.build_file(build_context, relpath)
    elif relpath.endswith(".css"):
        return vanillaplusjs.build.handlers.css.build_file(build_context, relpath)
    elif relpath.endswith(".js"):
        return vanillaplusjs.build.handlers.js.build_file(build_context, relpath)
    return vanillaplusjs.build.handlers.copy_and_hash.build_file(build_context, relpath)
