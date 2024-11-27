from typing import Any
import json
import yaml
from flextag.core.interfaces.parser import IContentParser
from flextag.logger import logger
from flextag.exceptions import FlexTagError


class TextParser(IContentParser):
    """Parser for plain text content"""

    def parse(self, content: str) -> str:
        """Pass through for text content"""
        return content.strip()

    def dump(self, data: Any) -> str:
        """Convert to string"""
        return str(data)


class JSONParser(IContentParser):
    """Parser for JSON content"""

    def parse(self, content: str) -> Any:
        """Parse JSON content"""
        try:
            if not content.strip():
                return {}
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}", content=content)
            raise FlexTagError(f"Invalid JSON content: {str(e)}")

    def dump(self, data: Any) -> str:
        """Convert to JSON string"""
        try:
            return json.dumps(data, indent=2)
        except TypeError as e:
            logger.error(f"JSON serialization error: {str(e)}", data=data)
            raise FlexTagError(f"Failed to serialize to JSON: {str(e)}")


class YAMLParser(IContentParser):
    """Parser for YAML content"""

    def parse(self, content: str) -> Any:
        """Parse YAML content"""
        try:
            if not content.strip():
                return {}
            result = yaml.safe_load(content)
            return {} if result is None else result
        except yaml.YAMLError:
            raise FlexTagError("Invalid YAML content")

    def dump(self, data: Any) -> str:
        """Convert to YAML string"""
        try:
            return yaml.safe_dump(data, sort_keys=False) if data else ""
        except yaml.YAMLError:
            raise FlexTagError("Failed to serialize to YAML")
