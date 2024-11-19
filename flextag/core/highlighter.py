# core/highlighter.py
import tkinter as tk
from typing import Dict, Optional, List

from flextag.core.interfaces.parser import TagInfo


class FlexTagHighlighter:
    def __init__(self, text_widget: tk.Text, colors: Optional[Dict[str, str]] = None):
        self.text = text_widget
        self.colors = colors or {
            "tag": "#0066aa",
            "comment": "#808080",
            "content": "#000000",
            "meta_key": "#994d00",
            "meta_value": "#0066aa",
            "error": "#ff0000",
        }

        self._setup_tags()

    def _setup_tags(self):
        for tag, color in self.colors.items():
            self.text.tag_configure(tag, foreground=color)

    def highlight(self, parser: "Parser", content: str):
        self._clear_tags()

        try:
            tag_infos = parser.parse_document(content)
            self._apply_highlighting(content, tag_infos)
            return None
        except Exception as e:
            return str(e)

    def _clear_tags(self):
        for tag in self.colors:
            self.text.tag_remove(tag, "1.0", "end")

    def _apply_highlighting(self, content: str, tag_infos: List[TagInfo]):
        lines = content.splitlines()
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            if line.startswith("[#]"):
                self.text.tag_add("comment", f"{i}.0", f"{i}.end")
                continue

            # Find matching tag info
            tag_info = next((t for t in tag_infos if t.line_number == i - 1), None)
            if tag_info:
                # Highlight tag
                tag_end = line.find("]") + 2
                self.text.tag_add("tag", f"{i}.0", f"{i}.{tag_end}")

                # Highlight metadata
                if len(line) > tag_end:
                    self._highlight_metadata(line[tag_end:], i, tag_end)
            else:
                self.text.tag_add("content", f"{i}.0", f"{i}.end")

    def _highlight_metadata(self, metadata_str: str, line_num: int, start_col: int):
        pos = start_col
        for part in metadata_str.strip().split():
            if "[" in part and "]" in part:
                key_end = part.index("[")
                if not part.startswith("["):  # Not shorthand
                    self.text.tag_add(
                        "meta_key", f"{line_num}.{pos}", f"{line_num}.{pos + key_end}"
                    )

                value_start = pos + key_end
                value_end = pos + len(part)
                self.text.tag_add(
                    "meta_value", f"{line_num}.{value_start}", f"{line_num}.{value_end}"
                )

            pos += len(part) + 1
