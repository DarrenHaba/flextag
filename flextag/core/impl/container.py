from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from ..base.container import BaseContainer
from .section import Section
from flextag.exceptions import ContainerError
from flextag.logger import logger
from flextag.settings import Const


@dataclass
class Container(BaseContainer):
    """Concrete implementation of FlexTag container"""
    metadata: Dict[str, Any] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=lambda: Const.DEFAULTS.copy())
    sections: List[Section] = field(default_factory=list)

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
                    container.params.update(cls._parse_parameters(line[len(Const.PARAMS_START):-2]))

                elif line.startswith(Const.META_START):
                    container.metadata.update(cls._parse_parameters(line[len(Const.META_START):-2]))

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
                params_str = " ".join(f'{k}="{v}"' if isinstance(v, str) else f"{k}={v}"
                                      for k, v in self.params.items())
                lines.append(f"{Const.PARAMS_START} {params_str}]]")

            # Add META section
            if self.metadata:
                meta_str = " ".join(f'{k}="{v}"' if isinstance(v, str) else f"{k}={v}"
                                    for k, v in self.metadata.items())
                lines.append(f"{Const.META_START} {meta_str}]]")

            # Add sections
            for section in self.sections:
                lines.append(section.to_string())

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Container serialization error: {str(e)}")
            raise ContainerError(f"Failed to serialize container: {str(e)}")
