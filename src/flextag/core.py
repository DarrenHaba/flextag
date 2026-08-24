"""FlexTag 0.5 — tags and sections for markdown. The whole thing, one file.

No syntax of its own: file metadata is YAML front matter, a section is a fenced
code block whose info string is a YAML flow mapping, and this module is only a
LOADER — parse, index, filter. PyYAML is the single dependency; there is no
FlexTag parser and no FlexTag highlighter, by design.

    view = load("books/")                     # a file or a whole directory
    view.filter(tag="strategy")               # sections by tag
    view.filter(id="daily-first-spark", version=2)
    view.values("status")                     # unique values -> dropdowns
    view.files(tag="daily")                   # FILES by front-matter tags

A file declares itself with `flextag: 0.5` in front matter — intent plus format
version, so future versions read old files knowingly. Files without the marker
still load: the loader indexes what is there.
"""
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

_FENCE = re.compile(r"^(`{3,}|~{3,})(\w[\w+-]*)?\s*(\{.*\})?\s*$")


class FlexTagError(Exception):
    """A file that cannot be read as it claims."""


@dataclass(eq=False)
class Section:
    """One tagged fence. `meta` is the info-string dictionary minus `tags`."""

    tags: list[str] = field(default_factory=list)
    meta: dict = field(default_factory=dict)
    lang: str = ""                 # the fence language = the body's type
    body: str = ""                 # verbatim
    file: str = ""
    line: int = 0                  # 1-based line of the opening fence

    def get(self, key: str, default=None):
        return self.meta.get(key, default)


@dataclass(eq=False)
class FileDoc:
    """One markdown file: its front matter and its sections."""

    path: str = ""
    tags: list[str] = field(default_factory=list)
    meta: dict = field(default_factory=dict)   # front matter minus `tags`
    sections: list[Section] = field(default_factory=list)

    @property
    def declared(self) -> str | None:
        """The `flextag:` front-matter marker, if the file carries one."""
        v = self.meta.get("flextag")
        return None if v is None else str(v)


class View:
    """Sections (and their files), filterable. Every filter returns a new View."""

    def __init__(self, docs: list[FileDoc]):
        self.docs = docs
        self.sections = [s for d in docs for s in d.sections]

    def filter(self, tag: str | None = None, **meta) -> "View":
        """Sections carrying `tag` (any segment of a `/` path matches) AND every
        `key=value` given. Chainable; case-sensitive on values, insensitive on tags."""
        out = []
        for d in self.docs:
            keep = [s for s in d.sections
                    if (tag is None or _tag_hit(s.tags, tag))
                    and all(s.meta.get(k) == v for k, v in meta.items())]
            if keep:
                out.append(FileDoc(d.path, d.tags, d.meta, keep))
        return View(out)

    def files(self, tag: str | None = None, **meta) -> list[FileDoc]:
        """FILES selected by front matter — the cross-file half of the old cascade."""
        return [d for d in self.docs
                if (tag is None or _tag_hit(d.tags, tag))
                and all(d.meta.get(k) == v for k, v in meta.items())]

    def values(self, key: str) -> list:
        """Unique values of `key` across matched sections — dropdowns, autocomplete."""
        seen = []
        for s in self.sections:
            v = s.meta.get(key)
            if v is not None and v not in seen:
                seen.append(v)
        return seen

    def tags(self) -> list[str]:
        seen: list[str] = []
        for s in self.sections:
            for t in s.tags:
                if t not in seen:
                    seen.append(t)
        return seen

    def children(self, prefix: str) -> list[str]:
        """Next path segment under `prefix` for `/`-spelled hierarchies:
        tags [dept/hardware/tools] -> children("dept") == ["hardware"]."""
        out: list[str] = []
        want = prefix.strip("/").lower()
        for t in self.tags() + [t for d in self.docs for t in d.tags]:
            parts = t.split("/")
            for i, p in enumerate(parts[:-1]):
                if p.lower() == want and parts[i + 1] not in out:
                    out.append(parts[i + 1])
        return out


def _tag_hit(tags: list[str], want: str) -> bool:
    w = want.strip("#/").lower()
    return any(w in (seg.lower() for seg in t.split("/")) for t in tags)


def _info_dict(raw: str, where: str) -> tuple[list[str], dict]:
    """The info string's `{...}` -> (tags, meta). It is YAML or it is an error —
    loudly, with the location, never a silently untagged section."""
    try:
        d = yaml.safe_load(raw)
    except yaml.YAMLError as ex:
        raise FlexTagError(f"{where}: fence attributes are not valid YAML: {ex}") from ex
    if not isinstance(d, dict):
        raise FlexTagError(f"{where}: fence attributes must be a YAML mapping, got {type(d).__name__}")
    tags = d.pop("tags", [])
    if isinstance(tags, str):
        tags = [tags]
    return [str(t) for t in tags], d


def load_file(path: str | Path) -> FileDoc:
    p = Path(path)
    lines = p.read_text(encoding="utf-8").split("\n")
    doc = FileDoc(path=str(p))
    i = 0
    if lines and lines[0].strip() == "---":                    # front matter
        j = next((k for k in range(1, len(lines)) if lines[k].strip() == "---"), -1)
        if j > 0:
            try:
                fm = yaml.safe_load("\n".join(lines[1:j])) or {}
            except yaml.YAMLError as ex:
                raise FlexTagError(f"{p}:1: front matter is not valid YAML: {ex}") from ex
            if not isinstance(fm, dict):
                raise FlexTagError(f"{p}:1: front matter must be a YAML mapping")
            tags = fm.pop("tags", [])
            doc.tags = [str(t) for t in ([tags] if isinstance(tags, str) else tags)]
            doc.meta = fm
            i = j + 1
    while i < len(lines):
        m = _FENCE.match(lines[i])
        if not m:
            i += 1
            continue
        ticks = m.group(1)
        close = next((k for k in range(i + 1, len(lines))
                      if lines[k].rstrip() == ticks), -1)
        if close < 0:
            raise FlexTagError(f"{p}:{i + 1}: unclosed fence")
        if m.group(3):                                         # tagged -> a section
            tags, meta = _info_dict(m.group(3), f"{p}:{i + 1}")
            doc.sections.append(Section(
                tags=tags, meta=meta, lang=m.group(2) or "text",
                body="\n".join(lines[i + 1:close]), file=str(p), line=i + 1))
        i = close + 1                                          # untagged -> prose
    return doc


def load(path: str | Path, recursive: bool = True) -> View:
    """A file, or every `.md` under a directory. Files that fail to parse raise —
    a broken file is a broken file, never a silently smaller index."""
    p = Path(path)
    if p.is_file():
        return View([load_file(p)])
    pattern = "**/*.md" if recursive else "*.md"
    return View([load_file(f) for f in sorted(p.glob(pattern))])
