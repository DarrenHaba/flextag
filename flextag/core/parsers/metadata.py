from typing import Dict, Any, Tuple
from flextag.core.types.metadata import Metadata
from flextag.logger import logger
from flextag.exceptions import FlexTagError


class MetadataParser:
    """Parser for metadata headers"""

    VALID_HEADER_TYPES = {'PARAMS', 'META', 'SEC'}
    PARAMETERS_ALLOW_EMPTY = {'crypt', 'comp', 'lang'}


    @classmethod
    def parse_header(cls, header: str) -> Tuple[str, Metadata]:
        """Parse [[PARAMS]], [[META]], or [[SEC]] header."""
        try:
            # Strip leading and trailing whitespace
            header = header.strip()

            # Remove [[ and ]]
            if not header.startswith('[[') or not header.endswith(']]'):
                raise FlexTagError("Header must start with '[[' and end with ']]'")
            header_content = header[2:-2].strip()
            logger.debug(f"Parsing header: {header_content}")

            # Split header content into parts
            parts = header_content.split()
            if not parts:
                raise FlexTagError("Empty header")

            # Get header type and optional ID
            type_and_id = parts[0]
            if ':' in type_and_id:
                header_type, section_id = type_and_id.split(':', 1)
                if not section_id:
                    raise FlexTagError("ID cannot be empty after ':'")
            else:
                header_type = type_and_id
                section_id = ''

            # Validate header type
            if header_type not in cls.VALID_HEADER_TYPES:
                raise FlexTagError(f"Invalid header type: '{header_type}'")

            # For PARAMS, IDs are not allowed
            if header_type == 'PARAMS' and section_id:
                raise FlexTagError("ID is not allowed in PARAMS header")

            # For META and SEC, IDs are optional but must be valid if present
            if header_type in {'META', 'SEC'} and section_id:
                if not cls._is_valid_id(section_id):
                    raise FlexTagError(f"Invalid ID '{section_id}' in {header_type} header")

            # Create metadata object
            metadata = Metadata(id=section_id)

            # Parse the remaining parts
            for part in parts[1:]:
                if header_type == 'PARAMS':
                    # In PARAMS, only key=value parameters are allowed
                    if '=' in part:
                        key, value = part.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if not key:
                            raise FlexTagError(f"Invalid parameter '{part}' in PARAMS header")
                        # Check if empty values are allowed for this key
                        if value == '' and key not in cls.PARAMETERS_ALLOW_EMPTY:
                            raise FlexTagError(f"Parameter '{key}' cannot have an empty value in PARAMS header")
                        parsed_value = cls._parse_parameter_value(value)
                        metadata.parameters[key] = parsed_value
                        logger.debug(f"Found parameter: {key}={parsed_value}")
                    else:
                        raise FlexTagError(f"Invalid content '{part}' in PARAMS header; only parameters are allowed")
                else:
                    # In META and SEC, handle tags, paths, and parameters
                    if part.startswith("#"):  # Tag
                        metadata.tags.append(part[1:])
                        logger.debug(f"Found tag: {part[1:]}")
                    elif part.startswith("."):  # Path
                        metadata.paths.append(part[1:])
                        logger.debug(f"Found path: {part[1:]}")
                    elif '=' in part:  # Parameter
                        key, value = part.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if not key or value == '':
                            raise FlexTagError(f"Invalid parameter '{part}' in {header_type} header")
                        parsed_value = cls._parse_parameter_value(value)
                        metadata.parameters[key] = parsed_value
                        logger.debug(f"Found parameter: {key}={parsed_value}")
                    else:
                        raise FlexTagError(f"Invalid content '{part}' in {header_type} header")
            return header_type, metadata

        except Exception as e:
            logger.error(f"Header parsing error: {str(e)}", extra={'header': header})
            raise FlexTagError(f"Failed to parse header: {str(e)}")

    @staticmethod
    def _is_valid_id(section_id: str) -> bool:
        """Check if the section ID is a valid identifier."""
        # IDs should not start with '#' or '.', and should not contain whitespace
        return not section_id.startswith(('#', '.')) and ' ' not in section_id

    @staticmethod
    def _parse_parameter_value(value: str) -> Any:
        """Attempt to parse parameter value to int, float, bool, or leave as string"""
        # Try to parse as boolean
        if value.lower() == 'true':
            return True
        if value.lower() == 'false':
            return False
        # Try to parse as integer
        try:
            int_value = int(value)
            return int_value
        except ValueError:
            pass
        # Try to parse as float
        try:
            float_value = float(value)
            return float_value
        except ValueError:
            pass
        # Return as string (including empty strings)
        return value

    def parse_params(self, header: str) -> Dict[str, Any]:
        """Parse [[PARAMS]] header"""
        try:
            header_type, metadata = self.parse_header(header)
            if header_type != 'PARAMS':
                raise FlexTagError("Header is not a PARAMS type")
            params = {
                "fmt": metadata.parameters.get('fmt', 'text'),
                "enc": metadata.parameters.get('enc', 'utf-8'),
                "crypt": metadata.parameters.get('crypt', ''),
                "comp": metadata.parameters.get('comp', ''),
                "lang": metadata.parameters.get('lang', 'en'),
            }
            # Include any additional parameters
            for key, value in metadata.parameters.items():
                if key not in params:
                    params[key] = value
            return params
        except Exception as e:
            logger.error(f"PARAMS parsing error: {str(e)}", extra={'header': header})
            raise FlexTagError(f"Failed to parse PARAMS: {str(e)}")

    def parse_meta(self, header: str) -> Metadata:
        """Parse [[META]] header"""
        try:
            header_type, metadata = self.parse_header(header)
            if header_type != 'META':
                raise FlexTagError("Header is not a META type")
            return metadata
        except Exception as e:
            logger.error(f"META parsing error: {str(e)}", extra={'header': header})
            raise FlexTagError(f"Failed to parse META: {str(e)}")

    def parse_section_meta(self, header: str) -> Metadata:
        """Parse [[SEC]] header"""
        try:
            header_type, metadata = self.parse_header(header)
            if header_type != 'SEC':
                raise FlexTagError("Header is not a SEC type")
            return metadata
        except Exception as e:
            logger.error(f"Section metadata parsing error: {str(e)}", extra={'header': header})
            raise FlexTagError(f"Failed to parse section metadata: {str(e)}")
