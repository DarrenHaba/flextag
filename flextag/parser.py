from typing import Union, Dict, List, Optional
import re
from .exceptions import (
    ParseError,
    WrapperError,
    TagError,
    StructureError,
    MissingWrapperError,
    InvalidTagError,
)


class Parser:
    """
    Internal parser implementation that only parses one level deep.
    Content indented 4 spaces after a tag is treated as raw string content,
    regardless of whether it contains FlexTag markup.
    """

    def __init__(self):
        self.start_marker = "<<--FLEXTAG_START-->>"
        self.end_marker = "<<--FLEXTAG_END-->>"
        self.tag_marker = "<<--"
        self.tag_terminator = ":"
        self.indent_size = 4

        # Build regex patterns
        marker = re.escape(self.tag_marker)
        brackets = r"(?:\[([^\]]*)\])+"  # One or more bracket pairs
        terminator = re.escape(self.tag_terminator)

        # Only match tags at exactly indent_size spaces
        self.section_pattern = re.compile(
            f"^\\s{{{self.indent_size}}}{marker}{brackets}{terminator}$"
        )
        self.start_pattern = re.compile(f"^{re.escape(self.start_marker)}$")
        self.end_pattern = re.compile(f"^{re.escape(self.end_marker)}$")

    def _extract_tag_parts(self, tag_str: str) -> list:
        """Extract all parts from bracket pairs in the tag"""
        parts = []
        bracket_pattern = re.compile(r"\[([^\]]*)\]")
        for match in bracket_pattern.finditer(tag_str):
            value = match.group(1)
            try:
                idx = int(value)
                parts.append(str(idx))  # Store as string for consistent handling
            except ValueError:
                parts.append(value)
        return parts

    def _strip_base_indent(self, lines: list[str]) -> str:
        """
        Strip exactly indent_size spaces from the start of content lines.
        Lines with less indentation will raise an error.
        """
        if not lines:
            return ""

        processed_lines = []
        for line in lines:
            if line.strip():  # If line has content
                # Verify content is properly indented
                if not line.startswith(" " * self.indent_size):
                    raise StructureError(
                        f"Content must be indented with exactly {self.indent_size} spaces",
                        example="""<<--[section]:
    Your content here with 4 spaces
    More content here with 4 spaces""",
                    )
                processed_lines.append(line[self.indent_size :])
            else:  # Keep empty lines as is
                processed_lines.append(line)

        return "\n".join(processed_lines)

    def parse(self, content: str) -> Union[Dict, List]:
        lines = content.strip().split("\n")
        root = {}
        current_path = []
        current_content = []
        in_flextag = False

        # Find the first START marker
        for i, line in enumerate(lines):
            if self.start_pattern.match(line.strip()):
                lines = lines[i:]
                break
        else:
            raise MissingWrapperError(
                "No START marker found", 1, content.split("\n")[0]
            )

        def store_current_content():
            if not current_path:
                return

            # Strip base indentation and store as raw string
            content_str = self._strip_base_indent(current_content)

            # For single-level parsing, current_path should always be length 1
            if len(current_path) != 1:
                raise StructureError(
                    "Invalid tag nesting - only one level of tags is supported",
                    example="""<<--[section1]:
    Content for section 1
<<--[section2]:
    Content for section 2""",
                )

            key = current_path[0]
            root[key] = content_str

        for line_number, line in enumerate(lines, 1):
            stripped = line.strip()

            # Handle START/END markers
            if self.start_pattern.match(stripped):
                if in_flextag:  # If we're already in FlexTag, treat as content
                    current_content.append(line)
                else:
                    in_flextag = True

            elif self.end_pattern.match(stripped):
                if current_path:  # If we have a current tag
                    store_current_content()
                if not in_flextag:
                    raise WrapperError("Unexpected END marker", line_number, line)
                in_flextag = False

            elif in_flextag:
                # Check for tag at base level (4 spaces indent)
                match = self.section_pattern.match(line)
                if match:
                    # Store previous section's content if any
                    if current_path:
                        store_current_content()

                    # Extract new path - should only be one level
                    try:
                        parts = self._extract_tag_parts(line)
                        if len(parts) != 1:
                            raise InvalidTagError(
                                "Only single-level tags are supported",
                                line_number,
                                line,
                            )
                        current_path = parts
                    except Exception as e:
                        raise InvalidTagError(
                            "Invalid tag format", line_number, line
                        ) from e
                    current_content = []
                else:
                    current_content.append(line)

        if in_flextag:
            raise MissingWrapperError("Missing END marker", len(lines), lines[-1])

        # Convert to list if appropriate
        if root and all(k.isdigit() for k in root.keys()):
            max_idx = max(int(k) for k in root.keys())
            result = [None] * (max_idx + 1)
            for k, v in root.items():
                result[int(k)] = v
            return result

        return root


def parse(content: str) -> Union[Dict, List]:
    """
    Parse FlexTag content into a Python data structure.

    Args:
        content (str): String containing FlexTag markup

    Returns:
        Union[Dict, List]: Parsed content structure - either a dictionary
        for named tags or a list for numeric tags

    Raises:
        ParseError: Base class for all parsing errors
        WrapperError: When START/END markers are invalid
        TagError: When tag format is invalid
        StructureError: When document structure is invalid

    Example:
        >>> import flextag
        >>> text = '''<<--FLEXTAG_START-->>
        ...     <<--[test]:
        ...     Hello World
        ... <<--FLEXTAG_END-->>'''
        >>> data = flextag.parse(text)
        >>> print(data)
        {'test': 'Hello World'}
    """
    return Parser().parse(content)
