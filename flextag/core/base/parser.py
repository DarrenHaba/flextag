from abc import ABC
from typing import Any, Dict, Type
from ..interfaces.parser import IContentParser, IFlexTagParser
from ..interfaces.container import IContainer
from flextag.exceptions import ContainerError
from flextag.logger import logger
from flextag.settings import Const


class BaseFlexTagParser(ABC, IFlexTagParser):
    """Base implementation of FlexTag parser with content format handling"""

    def __init__(self):
        self.content_parsers: Dict[str, Type[IContentParser]] = {}
        logger.debug("Initialized FlexTag parser")

    def register_content_parser(self, fmt: str, parser: Type[IContentParser]) -> None:
        """Register a parser for a specific content format"""
        self.content_parsers[fmt] = parser
        logger.debug(f"Registered content parser for format: {fmt}")

    def get_content_parser(self, fmt: str) -> IContentParser:
        """Get parser instance for format"""
        if fmt not in self.content_parsers:
            logger.error(f"No parser found for format: {fmt}")
            raise ContainerError(f"Unsupported content format: {fmt}")
        return self.content_parsers[fmt]()

    def parse_parameters(self, param_str: str) -> Dict[str, Any]:
        """Parse space-delimited parameters"""
        params = {}
        try:
            parts = param_str.split()
            for part in parts:
                if part.startswith("#"):  # Tag
                    params.setdefault("tags", []).append(part[1:])
                elif part.startswith("."):  # Path
                    params.setdefault("paths", []).append(part[1:])
                elif "=" in part:  # Key-value parameter
                    key, value = part.split("=", 1)
                    # Handle parameter types
                    if value.startswith('"') and value.endswith('"'):
                        params[key] = value[1:-1]  # String
                    elif value.lower() in ("true", "false"):
                        params[key] = value.lower() == "true"  # Boolean
                    elif "." in value:
                        params[key] = float(value)  # Float
                    elif value.isdigit():
                        params[key] = int(value)  # Integer
                    elif value.startswith("[") and value.endswith("]"):
                        params[key] = eval(value)  # Array
            return params
        except Exception as e:
            logger.error(f"Parameter parsing error: {str(e)}", param_str=param_str)
            raise ParameterError(f"Invalid parameter syntax: {param_str}")
