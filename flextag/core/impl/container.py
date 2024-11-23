from dataclasses import dataclass, field
from typing import Dict, List, Any

from .section import Section
from ..base.container import BaseContainer
from ..interfaces.section import ISection
from ...settings import Const
from ...exceptions import ContainerError
from ...logger import logger


@dataclass
class Container(BaseContainer):
    metadata: Dict[str, Any] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    sections: List[Section] = field(default_factory=list)

    def add_section(self, section: ISection) -> None:
        """Add a section to the container"""
        logger.debug(
            f"Adding section: id={section.id}, tags={section.tags}, paths={section.paths}"
        )
        if section not in self.sections:  # Avoid duplicates
            self.sections.append(section)
            logger.debug(f"Container now has {len(self.sections)} sections")

    @classmethod
    def from_string(cls, content: str) -> "Container":
        """Create container from FlexTag format"""
        try:
            container = cls()
            logger.debug("Starting container parsing")
            lines = content.splitlines()

            i = 0
            while i < len(lines):
                line = lines[i].strip()
                logger.debug(f"Parsing line: {line}")

                if line.startswith(Const.PARAMS_START):
                    param_str = line[len(Const.PARAMS_START) : -2].strip()
                    logger.debug(f"Found PARAMS: {param_str}")
                    container.params.update(cls._parse_parameters(param_str))

                elif line.startswith(Const.META_START):
                    meta_str = line[len(Const.META_START) : -2].strip()
                    logger.debug(f"Found META: {meta_str}")
                    container.metadata.update(cls._parse_parameters(meta_str))

                elif line.startswith(Const.SEC_START):
                    logger.debug(f"Found section start: {line}")
                    header = line
                    content_lines = []
                    i += 1
                    while i < len(lines) and not lines[i].strip().startswith(
                        Const.SEC_END
                    ):
                        content_lines.append(lines[i])
                        i += 1
                    logger.debug(f"Section content lines: {len(content_lines)}")

                    section = Section.from_header(header, "\n".join(content_lines))
                    logger.debug(
                        f"Created section: id={section.id}, tags={section.tags}, paths={section.paths}"
                    )
                    container.add_section(section)  # This should work now

                i += 1

            logger.debug(
                f"Finished parsing container. Sections: {len(container.sections)}"
            )
            return container

        except Exception as e:
            logger.error(f"Container parsing error: {str(e)}")
            raise ContainerError(f"Failed to parse container: {str(e)}")

    @staticmethod
    def _parse_parameters(param_str: str) -> Dict[str, Any]:
        """Parse space-delimited parameters into dictionary"""
        params = {}
        if not param_str.strip():
            return params

        try:
            parts = param_str.split()
            for part in parts:
                if part.startswith("#"):  # Tag
                    params.setdefault("tags", []).append(part[1:])
                elif part.startswith("."):  # Path
                    params.setdefault("paths", []).append(part[1:])
                elif "=" in part:  # Key-value parameter
                    key, value = part.split("=", 1)
                    key = key.strip()
                    value = value.strip()

                    # Handle quoted strings
                    if (value.startswith('"') and value.endswith('"')) or (
                        value.startswith("'") and value.endswith("'")
                    ):
                        params[key] = value[1:-1]
                    elif value.lower() in ("true", "false"):
                        params[key] = value.lower() == "true"
                    elif value.replace(".", "").isdigit():
                        params[key] = float(value) if "." in value else int(value)
                    else:
                        params[key] = value

            return params

        except Exception as e:
            logger.error(f"Parameter parsing error: {str(e)}", param_str=param_str)
            raise ContainerError(f"Failed to parse parameters: {str(e)}")
