from typing import Optional, Any, List


class FlexTagError(Exception):
    """Base exception for all FlexTag errors"""

    def __init__(
        self,
        message: str,
        line_number: Optional[int] = None,
        line_content: Optional[str] = None,
        additional_lines: Optional[List[str]] = None,
        example: Optional[str] = None,
    ):
        self.line_number = line_number
        self.line_content = line_content
        self.additional_lines = additional_lines or []
        self.example = example
        self.message = message

        # Build detailed error message
        details = [message]

        if line_number is not None:
            details.append(f"Line {line_number}")

        if line_content is not None:
            details.append(f"Content:")
            details.append(f"    {line_content}")
            for line in self.additional_lines:
                details.append(f"    {line}")

        if example is not None:
            details.append("\nCorrect example:")
            details.append(example)

        self.full_message = "\n".join(details)
        super().__init__(self.full_message)


class ParseError(FlexTagError):
    """Base class for parsing related errors"""

    pass


class WrapperError(ParseError):
    """Errors related to FlexTag wrapper markers"""

    pass


class TagError(ParseError):
    """Errors related to tag syntax"""

    pass


class StructureError(FlexTagError):
    """Errors related to document structure"""

    def __init__(
        self,
        message: str,
        line_number: Optional[int] = None,
        line_content: Optional[str] = None,
        additional_lines: Optional[List[str]] = None,
        example: Optional[str] = None,
    ):
        if example is None:
            example = """<<--FLEXTAG_START-->>
    <<--[section]:
    Your content here with 4 spaces
    More content here with 4 spaces
<<--FLEXTAG_END-->>"""

        super().__init__(message, line_number, line_content, additional_lines, example)


class SerializationError(FlexTagError):
    """Base class for serialization related errors"""

    def __init__(self, message: str, problematic_value: Any = None):
        self.problematic_value = problematic_value
        super().__init__(message)


class ValidationError(FlexTagError):
    """Errors related to data validation"""

    pass


# More specific error classes
class MissingWrapperError(WrapperError):
    """Raised when FlexTag wrapper markers are missing or mismatched"""

    pass


class InvalidTagError(TagError):
    """Raised when a tag has invalid syntax"""

    pass


class NestedTagError(TagError):
    """Raised when tags are improperly nested"""

    pass


class DuplicateTagError(TagError):
    """Raised when duplicate tags are found where not allowed"""

    pass


class UnserializableTypeError(SerializationError):
    """Raised when attempting to serialize unsupported types"""

    pass


class MalformedDataError(ValidationError):
    """Raised when data structure doesn't match expected format"""

    pass
