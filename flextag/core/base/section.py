from abc import ABC
from typing import List, Dict, Any
from dataclasses import dataclass, field
from ..interfaces.section import ISection
from flextag.settings import Const
from flextag.logger import logger
from flextag.exceptions import ParameterError


@dataclass
class BaseSection(ABC, ISection):
    """Base implementation of ISection with parameter handling"""

    id: str = ""
    tags: List[str] = field(default_factory=list)
    paths: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    content: str = ""

    # Required parameters with defaults
    fmt: str = Const.DEFAULTS["fmt"]
    enc: str = Const.DEFAULTS["enc"]
    crypt: str = Const.DEFAULTS["crypt"]
    comp: str = Const.DEFAULTS["comp"]
    lang: str = Const.DEFAULTS["lang"]

    def __post_init__(self):
        """Validate parameters after initialization"""
        self._validate_parameters()
        logger.debug(f"Initialized section {self.id}")

    def _validate_parameters(self):
        """Validate parameter types and values"""
        try:
            for key, value in self.parameters.items():
                if (
                    isinstance(value, str)
                    and value.startswith('"')
                    and value.endswith('"')
                ):
                    self.parameters[key] = value[1:-1]  # Strip quotes
                elif isinstance(value, (int, float, bool, list)):
                    continue
                else:
                    raise ParameterError(
                        f"Invalid parameter type for {key}: {type(value)}"
                    )
        except Exception as e:
            logger.error(f"Parameter validation error: {str(e)}", section_id=self.id)
            raise

    def matches(self, query: str) -> bool:
        """Match section against query"""
        try:
            parts = query.strip().split()
            for part in parts:
                if part.startswith("#"):  # Tag match
                    tag = part[1:]
                    if tag not in self.tags:
                        return False
                elif part.startswith("."):  # Path match
                    path = part[1:]
                    if not any(p.startswith(path) for p in self.paths):
                        return False
                elif "=" in part:  # Parameter match
                    key, value = part.split("=", 1)
                    if key not in self.parameters or str(self.parameters[key]) != value:
                        return False
                elif ">" in part or "<" in part:  # Numeric comparison
                    # Implement numeric parameter comparison
                    pass
            return True
        except Exception as e:
            logger.error(
                f"Query matching error: {str(e)}", query=query, section_id=self.id
            )
            return False

    def clone(self) -> "ISection":
        """Create independent copy of section"""
        return BaseSection(
            id=self.id,
            tags=self.tags.copy(),
            paths=self.paths.copy(),
            parameters=self.parameters.copy(),
            content=self.content,
            fmt=self.fmt,
            enc=self.enc,
            crypt=self.crypt,
            comp=self.comp,
            lang=self.lang,
        )
