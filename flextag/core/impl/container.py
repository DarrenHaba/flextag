from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

from ..base.container import BaseContainer
from ..impl.section import Section
from ...exceptions import ContainerError, ParameterError
from ...logger import logger
from ...settings import Const


@dataclass
class Container(BaseContainer):
    """Concrete implementation of FlexTag container"""
    metadata: Dict[str, Any] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=lambda: Const.DEFAULTS.copy())
    sections: List[Section] = field(default_factory=list)

    @staticmethod
    def _parse_parameters(param_str: str) -> Dict[str, Any]:
        """Parse space-delimited parameters into dictionary"""
        try:
            params = {}
            parts = []
            current = []
            in_quotes = False
            quote_char = None

            # First pass: handle quoted strings properly
            for char in param_str.strip():
                if char in ('"', "'"):
                    if not in_quotes:
                        in_quotes = True
                        quote_char = char
                    elif char == quote_char:
                        in_quotes = False
                        quote_char = None
                    current.append(char)
                elif char.isspace() and not in_quotes:
                    if current:
                        parts.append(''.join(current))
                        current = []
                else:
                    current.append(char)

            if current:
                parts.append(''.join(current))

            # Now process each part
            for part in parts:
                if part.startswith("#"):  # Tag
                    params.setdefault("tags", []).append(part[1:])
                elif part.startswith("."): # Path
                    params.setdefault("paths", []).append(part[1:])
                elif "=" in part:  # Key-value parameter
                    key, value = part.split("=", 1)
                    key = key.strip()
                    value = value.strip()

                    # Handle quoted strings
                    if (value.startswith('"') and value.endswith('"')) or \
                            (value.startswith("'") and value.endswith("'")):
                        params[key] = value[1:-1]  # Strip quotes
                    elif value.lower() in ('true', 'false'):
                        params[key] = value.lower() == 'true'
                    elif value.startswith('[') and value.endswith(']'):
                        values = []
                        for v in value[1:-1].split(','):
                            v = v.strip()
                            if (v.startswith('"') and v.endswith('"')) or \
                                    (v.startswith("'") and v.endswith("'")):
                                values.append(v[1:-1])
                            elif v.lower() in ('true', 'false'):
                                values.append(v.lower() == 'true')
                            elif '.' in v and v.replace('.', '').isdigit():
                                values.append(float(v))
                            elif v.isdigit():
                                values.append(int(v))
                            else:
                                values.append(v)
                        params[key] = values
                    elif '.' in value and value.replace('.', '').isdigit():
                        params[key] = float(value)
                    elif value.isdigit():
                        params[key] = int(value)
                    else:
                        params[key] = value

            return params

        except Exception as e:
            logger.error(f"Parameter parsing error: {str(e)}", param_str=param_str)
            raise ParameterError(f"Invalid parameter syntax: {str(e)}")

    @classmethod
    def from_string(cls, content: str) -> "Container":
        """Create container from FlexTag format"""
        try:
            container = cls()
            lines = content.splitlines()
            current_section = []

            i = 0
            while i < len(lines):
                line = lines[i].strip()

                if line.startswith(Const.PARAMS_START):
                    # Parse parameters after [[PARAMS and before ]]
                    param_str = line[len(Const.PARAMS_START):-2].strip()
                    container.params.update(cls._parse_parameters(param_str))

                elif line.startswith(Const.META_START):
                    # Parse metadata after [[META and before ]]
                    meta_str = line[len(Const.META_START):-2].strip()
                    container.metadata.update(cls._parse_parameters(meta_str))

                elif line.startswith(Const.SEC_START):
                    header = line
                    content_lines = []
                    i += 1
                    while i < len(lines) and not lines[i].strip().startswith(Const.SEC_END):
                        content_lines.append(lines[i])
                        i += 1
                    container.add_section(Section.from_header(header, "\n".join(content_lines)))

                i += 1

            return container

        except Exception as e:
            logger.error(f"Container parsing error: {str(e)}")
            raise ContainerError(f"Failed to parse container: {str(e)}")

    def to_string(self) -> str:
        """Convert container to FlexTag format"""
        try:
            lines = []

            # Add PARAMS section if any non-default params
            if any(self.params[k] != v for k, v in Const.DEFAULTS.items()):
                params_str = " ".join(self._format_parameter(k, v)
                                      for k, v in self.params.items())
                lines.append(f"{Const.PARAMS_START} {params_str}]]")

            # Add META section
            if self.metadata:
                meta_str = " ".join(self._format_parameter(k, v)
                                    for k, v in self.metadata.items())
                lines.append(f"{Const.META_START} {meta_str}]]")

            # Add sections
            for section in self.sections:
                lines.append(section.to_string())

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Container serialization error: {str(e)}")
            raise ContainerError(f"Failed to serialize container: {str(e)}")

    @staticmethod
    def _format_parameter(key: str, value: Any) -> str:
        """Format a single parameter as string"""
        if isinstance(value, str):
            return f'{key}="{value}"'
        elif isinstance(value, list):
            values = [f'"{v}"' if isinstance(v, str) else str(v) for v in value]
            return f'{key}=[{",".join(values)}]'
        else:
            return f"{key}={value}"
