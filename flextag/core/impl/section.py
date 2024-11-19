from dataclasses import dataclass, field
from typing import List, Dict, Any
from ..base.section import BaseSection


@dataclass
class Section(BaseSection):
    tags: List[str] = field(default_factory=list)
    paths: List[str] = field(default_factory=list)
    params: Dict[str, Any] = field(default_factory=dict)
    content: str = ""

    @classmethod
    def from_header(cls, header: str, content: str = "") -> "Section":
        # Remove [[ and ]] and split into parts
        header = header[2:-2].strip()
        type_, *parts = header.split()

        tags = []
        paths = []
        params = {}

        for part in parts:
            if part.startswith("{"):
                params = cls._parse_params(part)
            elif part.startswith("#"):
                tags.append(part[1:])
            elif part.startswith("."):
                paths.append(part[1:])

        return cls(tags=tags, paths=paths, params=params, content=content)

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
