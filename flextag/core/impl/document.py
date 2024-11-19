from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from ..base.document import BaseDocument
from .section import Section


@dataclass
class Document(BaseDocument):
    settings: Dict[str, Any] = field(default_factory=dict)
    info: Optional[Section] = None
    sections: List[Section] = field(default_factory=list)

    @classmethod
    def from_string(cls, content: str) -> "Document":
        doc = cls()
        lines = content.splitlines()
        current_section = []
        current_header = ""

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            if line.startswith("[[SETTINGS"):
                doc.settings = cls._parse_params(line[10:-2])  # -2 for ]]

            elif line.startswith("[[INFO"):
                header = line
                content_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("[[/INFO"):
                    content_lines.append(lines[i])
                    i += 1
                doc.info = Section.from_header(header, "\n".join(content_lines))

            elif line.startswith("[[SEC"):
                header = line
                content_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("[[/SEC"):
                    content_lines.append(lines[i])
                    i += 1
                doc.add_section(Section.from_header(header, "\n".join(content_lines)))

            i += 1

        return doc

    @staticmethod
    def _parse_params(param_str: str) -> Dict[str, Any]:
        if not param_str.strip():
            return {}

        params = {}
        param_str = param_str.strip("{}")

        for pair in param_str.split(","):
            if not pair.strip():
                continue
            key, value = pair.split("=")
            key = key.strip()
            value = value.strip().strip('"')

            # Type inference
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            elif value.replace(".", "").isdigit():
                value = float(value) if "." in value else int(value)

            params[key] = value

        return params

    def to_string(self) -> str:
        lines = []

        if self.settings:
            params = ", ".join(
                f'{k}="{v}"' if isinstance(v, str) else f"{k}={v}"
                for k, v in self.settings.items()
            )
            lines.append(f"[[SETTINGS {{{params}}}]]")

        if self.info:
            lines.append(self._format_section(self.info, "INFO"))

        for section in self.sections:
            lines.append(self._format_section(section, "SEC"))

        return "\n".join(lines)

    def _format_section(self, section: Section, type_: str) -> str:
        lines = []

        # Format header with tags, paths, and params
        header_parts = []
        header_parts.extend(f"#{tag}" for tag in section.tags)
        header_parts.extend(f".{path}" for path in section.paths)

        if section.params:
            params = ", ".join(
                f'{k}="{v}"' if isinstance(v, str) else f"{k}={v}"
                for k, v in section.params.items()
            )
            header_parts.append(f"{{{params}}}")

        lines.append(f"[[{type_} {' '.join(header_parts)}]]")

        if section.content:
            lines.append(section.content)

        lines.append(f"[[/{type_}]]")

        return "\n".join(lines)
