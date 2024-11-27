from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from .parameter import ParameterValue, ParameterType
from ...exceptions import ParameterError
from ...logger import logger


@dataclass
class MetadataParameters:
    """Default parameters that apply to both metadata and sections"""
    fmt: str = "text"     # Format type
    enc: str = "utf-8"    # Encoding
    crypt: str = ""       # Encryption method
    comp: str = ""        # Compression method
    lang: str = "en"      # Language


@dataclass
class Metadata(MetadataParameters):
    """Common metadata structure for both sections and containers"""
    id: str = ""
    tags: List[str] = field(default_factory=list)
    paths: List[str] = field(default_factory=list)
    parameters: Dict[str, ParameterValue] = field(default_factory=dict)

    def add_parameter(self, key: str, raw_value: str) -> None:
        """Add a parameter with proper type inference"""
        try:
            self.parameters[key] = ParameterValue.parse(raw_value)
            logger.debug(
                f"Added parameter: {key}={self.parameters[key].to_string()} "
                f"(type: {self.parameters[key].type})"
            )
        except Exception as e:
            logger.error(f"Failed to add parameter: {str(e)}",
                         key=key, value=raw_value)
            raise ParameterError(f"Failed to add parameter '{key}': {str(e)}")

    def get_parameter(self, key: str) -> Optional[Any]:
        """Get parameter value, returns None if not found"""
        param = self.parameters.get(key)
        return param.value if param else None

    def get_parameter_type(self, key: str) -> Optional[ParameterType]:
        """Get parameter type, returns None if not found"""
        param = self.parameters.get(key)
        return param.type if param else None

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary"""
        return {
            "id": self.id,
            "tags": self.tags.copy(),
            "paths": self.paths.copy(),
            "parameters": {
                k: v.to_string() for k, v in self.parameters.items()
            },
            "fmt": self.fmt,
            "enc": self.enc,
            "crypt": self.crypt,
            "comp": self.comp,
            "lang": self.lang
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Metadata':
        """Create metadata from dictionary"""
        try:
            metadata = cls(
                id=data.get("id", ""),
                fmt=data.get("fmt", "text"),
                enc=data.get("enc", "utf-8"),
                crypt=data.get("crypt", ""),
                comp=data.get("comp", ""),
                lang=data.get("lang", "en")
            )

            metadata.tags = data.get("tags", [])
            metadata.paths = data.get("paths", [])

            # Parse parameters
            for key, value in data.get("parameters", {}).items():
                metadata.add_parameter(key, value)

            return metadata

        except Exception as e:
            logger.error(f"Failed to create metadata from dict: {str(e)}",
                         data=data)
            raise ParameterError(
                f"Failed to create metadata from dictionary: {str(e)}"
            )
