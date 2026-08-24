"""FlexTag — tags and sections for markdown.

Ordinary markdown files; machine content in fenced code blocks; a YAML mapping
on the fence line tags each block. `load()` reads a file or a whole folder
tree and returns every tagged section as one filterable dataset.

    import flextag
    view = flextag.load("configs/")
    view.filter(tag="database", id="prod-db")

The deprecated 0.4 container (`[[#tag ...]]: type` in `.ft` files) remains
readable during migration via `from flextag import legacy` — it is frozen and
removed at 0.6.
"""

from .core import (
    FileDoc,
    FlexTagError,
    Section,
    View,
    load,
    load_file,
)

__version__ = "0.5.0a1"

#: The FORMAT version files declare in front matter (`flextag: 0.5`) —
#: intentionally coarser than the package version.
FORMAT_VERSION = "0.5"

__all__ = ["FileDoc", "FlexTagError", "Section", "View", "load", "load_file",
           "FORMAT_VERSION", "__version__"]
