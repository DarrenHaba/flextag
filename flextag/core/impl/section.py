from dataclasses import dataclass, field
from typing import List, Dict, Any

from ..base.section import BaseSection
from ...exceptions import ParameterError
from ...logger import logger
from ...settings import Const


@dataclass
class Section(BaseSection):
    id: str = ""
    tags: List[str] = field(default_factory=list)
    paths: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    content: str = ""

    @classmethod
    def from_header(cls, header: str, content: str = "") -> "Section":
        """Create section from header string"""
        try:
            # Remove [[ and ]]
            header = header[2:-2].strip()
            logger.debug(f"Parsing header: {header}")

            # Check for ID first - it must be immediately after SEC: or META:
            section_id = ""
            if ":" in header:
                type_and_id, header = header.split(" ", 1)
                if ":" in type_and_id:
                    section_id = type_and_id.split(":", 1)[1]
                    logger.debug(f"Found section ID: {section_id}")

            # Initialize collections
            tags = []
            paths = []
            parameters = {}

            # Parse space-delimited parts
            for part in header.strip().split():
                if part.startswith("#"):
                    tags.append(part[1:])  # Store without #
                elif part.startswith("."):
                    paths.append(part[1:])  # Store without .
                elif "=" in part:
                    key, value = part.split("=", 1)
                    # Handle parameter values
                    value = value.strip()
                    if (value.startswith('"') and value.endswith('"')) or (
                        value.startswith("'") and value.endswith("'")
                    ):
                        parameters[key.strip()] = value[1:-1]  # String
                    elif value.lower() in ("true", "false"):
                        parameters[key.strip()] = value.lower() == "true"  # Boolean
                    elif value.startswith("[") and value.endswith("]"):
                        # Array - simple split for now
                        values = [
                            v.strip().strip("\"'") for v in value[1:-1].split(",")
                        ]
                        parameters[key.strip()] = values
                    elif "." in value and value.replace(".", "").isdigit():
                        parameters[key.strip()] = float(value)  # Float
                    elif value.isdigit():
                        parameters[key.strip()] = int(value)  # Integer
                    else:
                        parameters[key.strip()] = value  # Raw string

            return cls(
                id=section_id,
                tags=tags,
                paths=paths,
                parameters=parameters,
                content=content,
            )

        except Exception as e:
            logger.error(f"Section header parsing error: {str(e)}", header=header)
            raise ParameterError(f"Failed to parse section header: {str(e)}")

    # @classmethod
    # def from_header(cls, header: str, content: str = "") -> "Section":
    #     """Create section from header string"""
    #     try:
    #         # Remove [[ and ]] and split into parts
    #         header = header[len(Const.SEC_START):-2].strip()
    #
    #         # Parse section ID if present
    #         section_id = ""
    #         if ":" in header:
    #             section_id, header = header.split(":", 1)
    #
    #         # Initialize collections
    #         tags = []
    #         paths = []
    #         parameters = {}
    #
    #         # Parse space-delimited parts
    #         for part in header.strip().split():
    #             if part.startswith("#"):  # Tag
    #                 tags.append(part[1:])
    #             elif part.startswith("."): # Path
    #                 paths.append(part[1:])
    #             elif "=" in part:  # Parameter
    #                 key, value = part.split("=", 1)
    #                 key = key.strip()
    #                 value = value.strip()
    #
    #                 # Parse value based on type
    #                 if (value.startswith('"') and value.endswith('"')) or \
    #                         (value.startswith("'") and value.endswith("'")):
    #                     parameters[key] = value[1:-1]  # String
    #                 elif value.lower() in ('true', 'false'):
    #                     parameters[key] = value.lower() == 'true'  # Boolean
    #                 elif value.startswith('[') and value.endswith(']'):
    #                     # Array
    #                     values = []
    #                     for v in value[1:-1].split(','):
    #                         v = v.strip()
    #                         if (v.startswith('"') and v.endswith('"')) or \
    #                                 (v.startswith("'") and v.endswith("'")):
    #                             values.append(v[1:-1])
    #                         elif v.lower() in ('true', 'false'):
    #                             values.append(v.lower() == 'true')
    #                         elif '.' in v and v.replace('.', '').isdigit():
    #                             values.append(float(v))
    #                         elif v.isdigit():
    #                             values.append(int(v))
    #                         else:
    #                             values.append(v)
    #                     parameters[key] = values
    #                 elif '.' in value and value.replace('.', '').isdigit():
    #                     parameters[key] = float(value)  # Float
    #                 elif value.isdigit():
    #                     parameters[key] = int(value)  # Integer
    #                 else:
    #                     parameters[key] = value  # Raw string
    #
    #         return cls(
    #             id=section_id,
    #             tags=tags,
    #             paths=paths,
    #             parameters=parameters,
    #             content=content
    #         )
    #
    #     except Exception as e:
    #         logger.error(f"Section header parsing error: {str(e)}", header=header)
    #         raise ParameterError(f"Failed to parse section header: {str(e)}")
