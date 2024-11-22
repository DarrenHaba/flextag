from dataclasses import dataclass, field
from typing import List, Dict, Any
from ..base.section import BaseSection
from flextag.exceptions import ParameterError
from flextag.logger import logger
from flextag.settings import Const


@dataclass
class Section(BaseSection):
    """Concrete implementation of FlexTag section"""
    id: str = ""
    tags: List[str] = field(default_factory=list)
    paths: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    content: str = ""

    # Required parameters
    fmt: str = Const.DEFAULTS["fmt"]
    enc: str = Const.DEFAULTS["enc"]
    crypt: str = Const.DEFAULTS["crypt"]
    comp: str = Const.DEFAULTS["comp"]
    lang: str = Const.DEFAULTS["lang"]

    @classmethod
    def from_header(cls, header: str, content: str = "") -> "Section":
        """Create section from header string"""
        try:
            # Remove [[ and ]] and split into parts
            header = header[len(Const.SEC_START):-2].strip()

            # Parse section ID if present
            if ":" in header:
                section_id, header = header.split(":", 1)
            else:
                section_id = ""

            parts = header.strip().split()

            tags = []
            paths = []
            parameters = {}

            # Parse space-delimited parameters
            for part in parts:
                if part.startswith("#"):
                    tags.append(part[1:])
                elif part.startswith("."):
                    paths.append(part[1:])
                elif "=" in part:
                    key, value = part.split("=", 1)
                    parameters[key] = cls._parse_value(value)

            return cls(
                id=section_id,
                tags=tags,
                paths=paths,
                parameters=parameters,
                content=content
            )

        except Exception as e:
            logger.error(f"Section parsing error: {str(e)}", header=header)
            raise ParameterError(f"Invalid section header format: {header}")

    @staticmethod
    def _parse_value(value: str) -> Any:
        """Parse parameter value to appropriate type"""
        value = value.strip()

        # String (quoted)
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]

        # Boolean
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False

        # Array
        if value.startswith("[") and value.endswith("]"):
            return [v.strip().strip('"') for v in value[1:-1].split(",")]

        # Number
        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError:
            return value

    def to_string(self) -> str:
        """Convert section to string format"""
        try:
            # Build header parts
            parts = []
            if self.id:
                parts.append(f"{Const.SEC_START}:{self.id}")
            else:
                parts.append(Const.SEC_START)

            # Add tags and paths
            parts.extend(f"#{tag}" for tag in self.tags)
            parts.extend(f".{path}" for path in self.paths)

            # Add parameters
            for key, value in self.parameters.items():
                if isinstance(value, str):
                    parts.append(f'{key}="{value}"')
                else:
                    parts.append(f"{key}={value}")

            header = f"{' '.join(parts)}]]"

            # Combine with content
            if self.content:
                return f"{header}\n{self.content}\n{Const.SEC_END}"
            return f"{header}\n{Const.SEC_END}"

        except Exception as e:
            logger.error(f"Section serialization error: {str(e)}")
            raise ParameterError(f"Failed to serialize section: {str(e)}")
