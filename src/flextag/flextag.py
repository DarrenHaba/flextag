import json
import logging
import os
import re
import shlex
from typing import (
    Any,
)

##############################################################################
# LOGGING
##############################################################################

logger = logging.getLogger("FlexTag")
logger.addHandler(logging.NullHandler())
# logger = logging.getLogger("FlexTag")
# logger.setLevel(logging.DEBUG)
# if not logger.handlers:
#     ch = logging.StreamHandler(stream=sys.stdout)
#     ch.setLevel(logging.DEBUG)
#     fmt = logging.Formatter("[%(levelname)s] %(name)s: %(message)s")
#     ch.setFormatter(fmt)
#     logger.addHandler(ch)

##############################################################################
# EXCEPTIONS
##############################################################################


class FlexTagError(Exception):
    """Base exception for FlexTag errors."""


class FlexTagSyntaxError(FlexTagError):
    """Raised for syntax issues with enhanced position tracking."""

    def __init__(
        self,
        message: str,
        line_num: int = -1,
        column_num: int = -1,
        source_name: str = "",
        line_content: str = "",
    ):
        # Format message with location info
        loc_info = []
        if source_name:
            loc_info.append(source_name)
        if line_num > 0:
            loc_info.append(f"L{line_num}")
        if column_num > 0:
            loc_info.append(f"C{column_num}")

        loc_str = " ".join(loc_info)
        msg = f"[{loc_str}] {message}" if loc_str else message

        # Add visual error pointer if we have line content and column
        if line_content and column_num > 0:
            msg += f"\n\n{line_content}\n"
            caret_pos = min(column_num - 1, len(line_content))
            caret_line = " " * caret_pos + "^"
            msg += caret_line

        super().__init__(msg)
        self.line_num = line_num
        self.column_num = column_num
        self.source_name = source_name
        self.line_content = line_content


class SchemaValidationError(FlexTagError):
    """Base class for schema validation errors with enhanced location tracking."""

    def __init__(
        self,
        message: str,
        source_file: str = "",
        line_num: int = -1,
        column_num: int = -1,
    ):
        loc_info = []
        if source_file:
            loc_info.append(source_file)
        if line_num > 0:
            loc_info.append(f"L{line_num}")
        if column_num > 0:
            loc_info.append(f"C{column_num}")

        loc_str = " ".join(loc_info)
        msg = f"[{loc_str}] {message}" if loc_str else message

        super().__init__(msg)
        self.source_file = source_file
        self.line_num = line_num
        self.column_num = column_num


class SchemaTypeError(SchemaValidationError):
    """Raised when a parameter or content field doesn't match the expected type."""


class SchemaSectionError(SchemaValidationError):
    """Missing required section, wrong order, or other structural schema issues."""


##############################################################################
# SETTINGS
##############################################################################


class FlexTagSettings:
    """
    Holds global settings controlling security options and parse limits.
    """

    def __init__(self):
        self._allow_directory_traversal = False
        self._allow_remote_loading = False
        self._max_section_size = 1024 * 1024  # 1MB
        self._max_nesting_depth = 50
        self._encoding = "utf-8"

    @property
    def allow_directory_traversal(self) -> bool:
        return self._allow_directory_traversal

    @allow_directory_traversal.setter
    def allow_directory_traversal(self, val: bool):
        self._allow_directory_traversal = val

    @property
    def allow_remote_loading(self) -> bool:
        return self._allow_remote_loading

    @allow_remote_loading.setter
    def allow_remote_loading(self, val: bool):
        self._allow_remote_loading = val

    @property
    def max_section_size(self) -> int:
        return self._max_section_size

    @max_section_size.setter
    def max_section_size(self, val: int):
        self._max_section_size = val

    @property
    def max_nesting_depth(self) -> int:
        return self._max_nesting_depth

    @max_nesting_depth.setter
    def max_nesting_depth(self, val: int):
        self._max_nesting_depth = val

    @property
    def encoding(self) -> str:
        return self._encoding

    @encoding.setter
    def encoding(self, val: str):
        self._encoding = val


##############################################################################
# CONTENT TYPES
##############################################################################

# Basic content types (non-markup)
BASIC_TYPES = {"text", "binary"}

##############################################################################
# PARSING HELPERS
##############################################################################

OP_PATTERN = re.compile(r"^([^=!<>]+)\s*(=|!=|>=|<=|>|<)\s*(.+)$")


def match_tag(pattern: str, tags: list[str]) -> bool:
    """
    Match a single tag pattern against a list of tags.

    Uses the same syntax as filter queries:
      #tag   = exact match (default)
      #tag*  = self + all descendants
      #tag+  = immediate children only

    This is the shared matching logic used by both schema matching
    and filter queries.
    """
    # Strip # prefix from pattern
    pat = pattern.lstrip("#")

    # Detect modifier suffix
    modifier = None
    if pat.endswith("*"):
        modifier = "*"
        pat = pat[:-1]
    elif pat.endswith("+"):
        modifier = "+"
        pat = pat[:-1]

    for tag in tags:
        tag_value = tag.lstrip("#")

        if modifier == "*":
            # Self + all descendants
            if tag_value == pat or tag_value.startswith(pat + "."):
                return True
        elif modifier == "+":
            # Immediate children only
            if tag_value.startswith(pat + "."):
                remainder = tag_value[len(pat) + 1:]
                if "." not in remainder:
                    return True
        else:
            # Exact match (default)
            if tag_value == pat:
                return True

    return False


def format_error_location(source_name, line_num, column_num):
    """Create standardized location string for errors."""
    parts = []
    if source_name:
        parts.append(source_name)
    if line_num > 0:
        parts.append(f"L{line_num}")
    if column_num > 0:
        parts.append(f"C{column_num}")
    return "[" + " ".join(parts) + "]" if parts else ""


def add_error_pointer(line_content, column_num):
    """Create visual pointer to error location."""
    if not line_content or column_num <= 0:
        return ""
    caret_pos = min(column_num - 1, len(line_content))
    return f"\n{line_content}\n{' ' * caret_pos}^"


def _collect_multiline_bracket_block(
    lines: list[str],
    start_index: int,
    source_name: str,
    open_seq: str = "[[",
    close_seq: str = "]]",
) -> (str, int):
    """
    Collects everything from 'lines[start_index]' onward until we find a
    line containing the corresponding close_seq (e.g. ']]' for double-bracket).

    We allow the bracket opener to be partial. Example:
        Line 1:  [[#tag
        Line 2:   param="val" /]]
    We'll return the entire bracket text (minus the outer brackets) as a string,
    and the new 'index' after consuming these lines.

    :param lines: All lines of the file/string.
    :param start_index: Where we found the first line containing the open_seq.
    :param source_name: For error messages
    :param open_seq: By default '[['
    :param close_seq: By default ']]'
    :return: (bracket_text, next_index)
             bracket_text => everything between the bracket pairs (not including them).
             next_index   => the line index after finishing the bracket block.
    :raises FlexTagSyntaxError if we never find the closing bracket.
    """

    i = start_index
    line = lines[i].rstrip("\n")

    # 1 Verify the line actually contains the open_seq
    if open_seq not in line:
        raise FlexTagSyntaxError(
            f"Expected '{open_seq}' at line {i+1} but not found.",
            line_num=i + 1,
            column_num=1,  # Start of line
            source_name=source_name,
            line_content=line,
        )

    # Find the open_seq position
    start_pos = line.index(open_seq)
    content_start_pos = start_pos + len(open_seq)

    # 2 Check if the *same line* also has close_seq
    if close_seq in line[content_start_pos:]:
        end_pos = line.rindex(close_seq)
        # Check for trailing content after close_seq
        trailing = line[end_pos + len(close_seq) :]
        if trailing.strip():
            trailing_col = end_pos + len(close_seq) + 1
            raise FlexTagSyntaxError(
                "Multiple type declarations",
                line_num=i + 1,
                column_num=trailing_col,
                source_name=source_name,
                line_content=line,
            )
        bracket_text = line[start_pos:end_pos].strip()
        i += 1
        return bracket_text, i
    else:
        # 3 Multi-line scenario:
        buffer = [line]  # store the first line
        i += 1

        found_close = False
        close_line_index = i  # will store the line where close_seq was found
        while i < len(lines):
            current = lines[i].rstrip("\n")
            buffer.append(current)
            if close_seq in current:
                found_close = True
                close_line_index = i
                i += 1
                break
            i += 1

        if not found_close:
            raise FlexTagSyntaxError(
                f"Missing closing '{close_seq}' for bracket block.",
                line_num=len(lines),
                source_name=source_name,
            )

        # Join all lines, then extract the text between first open_seq and final close_seq
        bracket_full = "\n".join(buffer)
        start_pos_2 = bracket_full.index(open_seq) + len(open_seq)
        end_pos_2 = bracket_full.rindex(close_seq)
        # check for extra trailing content after the closing bracket.
        trailing = bracket_full[end_pos_2 + len(close_seq) :]
        if trailing.strip():
            raise FlexTagSyntaxError(
                "Multiple type declarations",
                line_num=close_line_index + 1,
                source_name=source_name,
            )
        bracket_text = bracket_full[start_pos_2:end_pos_2].strip()
        return bracket_text, i


def parse_basic_value(s: str):
    """
    Converts a string to bool, None, int, float **only** if the stripped
    content clearly matches one of those. Otherwise returns the original
    string (preserving any leading/trailing spaces).
    """
    # For checking special keywords or numeric form, we look at the stripped version
    st = s.strip()
    st_lower = st.lower()

    # Booleans or null
    if st_lower == "true":
        return True
    if st_lower == "false":
        return False
    if st_lower == "null":
        return None

    # Numeric?
    if st:  # non-empty
        # Try int
        try:
            return int(st)
        except ValueError:
            pass
        # Try float
        try:
            return float(st)
        except ValueError:
            pass

    # If nothing matched => return the original string, preserving spaces
    return s


def compare_op(lhs: Any, rhs: Any, op: str) -> bool:
    """
    Compare two values using the operator from the query syntax.
    """
    if op == "=":
        return lhs == rhs
    if op == "!=":
        return lhs != rhs
    try:
        lf, rf = float(lhs), float(rhs)
    except (ValueError, TypeError):
        return False
    if op == ">":
        return lf > rf
    if op == ">=":
        return lf >= rf
    if op == "<":
        return lf < rf
    if op == "<=":
        return lf <= rf
    return False


def _interpret_bracket_meta(
    bracket_str: str, line_num: int = -1, source_name: str = "", original_line: str = ""
):
    """
    A standard bracket-metadata parser using shlex.
    e.g. "default_param1=123 #tag .path /" -> (id, [#tag], [.path], {default_param1:123}, is_self_closing)

    Tracks line and column numbers for detailed error reporting.
    """
    bracket_str = bracket_str.strip()
    logger.debug(f"Interpreting bracket meta: {bracket_str!r}")

    is_self_closing = False
    if bracket_str.endswith("/"):
        is_self_closing = True
        bracket_str = bracket_str[:-1].strip()
        logger.debug(f"Self-closing detected. Stripped bracket: {bracket_str!r}")

    try:
        tokens = shlex.split(bracket_str)
        logger.debug(f"Tokens: {tokens!r}")
    except ValueError as e:
        # Extract column information from shlex error
        error_msg = str(e)
        column_num = 1  # Default position

        # shlex errors often indicate the position with messages like:
        # "No closing quotation at position 10"
        position_match = re.search(r"position (\d+)", error_msg)
        if position_match:
            # The position in the error is relative to bracket_str
            # We need to adjust for any indentation in the original line
            pos_in_bracket = int(position_match.group(1))

            if original_line:
                # Find where bracket_str starts in original_line
                start_idx = original_line.find(bracket_str.split()[0])
                if start_idx >= 0:
                    column_num = (
                        start_idx + pos_in_bracket + 1
                    )  # +1 for 1-based indexing
                else:
                    column_num = pos_in_bracket + 1
            else:
                column_num = pos_in_bracket + 1

    section_id = ""
    tags = []
    params = {}

    # Special handling for '[' as a separate token
    if tokens and tokens[0] == "[":
        tokens = tokens[1:]  # Skip the opening bracket token

    if tokens:
        first = tokens[0]
        if first.startswith("[#"):
            # Extract the tag part
            tags.append("#" + first[2:])
            tokens = tokens[1:]
        elif first.startswith("[@"):
            # Legacy @ prefix - convert to #tag
            tags.append("#" + first[2:])
            tokens = tokens[1:]
        elif first.startswith("[") and "=" in first:
            # Handle parameter with bracket: "[param=value"
            param_part = first[1:]  # Remove the bracket
            k, v = param_part.split("=", 1)
            params[k.strip()] = parse_basic_value(v)
            tokens = tokens[1:]
        elif (
            not first.startswith("#")
            and not first.startswith("@")
            and not first.startswith(".")
            and "=" not in first
        ):
            section_id = first
            tokens = tokens[1:]

    # Process the rest of the tokens
    for t in tokens:
        if t.startswith("#") or t.startswith("!#"):
            tags.append(t)
        elif t.startswith("@"):
            # Legacy @ prefix - convert to #tag
            tags.append("#" + t[1:])
        elif t.startswith("."):
            # Deprecated path syntax - convert to #tag
            logger.warning(
                f"Deprecated path syntax '.{t[1:]}' used. "
                f"Please use '#{t[1:]}' instead."
            )
            tags.append("#" + t[1:])
        elif "=" in t:
            k, v = t.split("=", 1)
            params[k.strip()] = parse_basic_value(v)
        else:
            # Bare token => param=True
            params[t] = True

    logger.debug(f"Default tags: {tags}")
    logger.debug(f"Default params: {params}")
    return (section_id, tags, params, is_self_closing)


def _parse_defaults_block(defaults_section) -> (str, list, dict):
    """
    Finds the first bracket block [ ... ] in the defaults section's content
    (which may span multiple lines). Returns (d_id, d_tags, d_params).
    """
    content_lines = defaults_section.raw_content.splitlines()
    i = 0
    n = len(content_lines)
    found_block = False
    bracket_str = ""
    original_line = ""  # Store the original line for error reporting

    # We only want the *first* bracket block in the defaults content (if any).
    while i < n:
        line = content_lines[i].rstrip("\n")
        if not line.strip() or line.strip().startswith("#"):
            # Skip blank or comment
            i += 1
            continue

        # Check if this line starts the bracket block
        if line.strip().startswith("["):
            original_line = line  # Save the original line before advancing i
            # Collect the bracket block with single bracket mode
            bracket_str, new_i = _collect_multiline_bracket_block(
                content_lines,
                i,
                defaults_section.source_name,
                open_seq="[",
                close_seq="]",
            )
            i = new_i
            found_block = True
            break
        else:
            i += 1

    if not found_block or not bracket_str.strip():
        # Means no bracket block was found
        return "", [], {}

    # Now parse that bracket string with your standard method:
    d_id, tags, params, _ = _interpret_bracket_meta(
        bracket_str,
        line_num=i,  # Use the index we saved
        source_name=defaults_section.source_name,
        original_line=original_line,  # Use the saved original line
    )
    return d_id, tags, params


##############################################################################
# PROPERTY SCHEMA (Tag-based schema system for header property validation)
##############################################################################


class PropertySchema:
    """
    Defines validation rules for sections matching specific tags.

    Schema tags use the SAME syntax as filter queries:
      #tag   = exact match (default)
      #tag*  = self + all descendants
      #tag+  = immediate children only
      !#tag  = negation (must NOT have tag)

    Examples:
        [[#adapter]]: ftml-schema            — matches only sections with exactly #adapter
        [[#adapter*]]: ftml-schema           — matches #adapter, #adapter.live, #adapter.live.binance, etc.
        [[#adapter+]]: ftml-schema           — matches #adapter.live, #adapter.historical (one level)
        [[#adapter #live]]: ftml-schema      — matches sections with BOTH exact #adapter AND exact #live
        [[#adapter !#deprecated]]: ftml-schema — matches sections with #adapter but NOT #deprecated

    TWO SEPARATE VALIDATIONS occur:
    1. Header properties are validated against the schema
    2. If the section's content type is 'ftml', the FTML body content is ALSO
       validated against the same schema
    """

    def __init__(
        self,
        tags: list[str],
        property_definitions: str,
        source_section: "Section",
    ):
        self.tags = tags  # e.g., ["#adapter*", "#live"]
        self.property_definitions = property_definitions  # FTML schema content
        self.source_section = source_section

    def __repr__(self):
        return f"<PropertySchema tags={self.tags}>"

    def matches_section(self, section: "Section") -> bool:
        """
        Check if this schema applies to the given section.

        Uses the same tag matching syntax as filter queries:
          #tag   = exact match (default)
          #tag*  = self + all descendants
          #tag+  = immediate children only
          !#tag  = negation (must NOT have tag)

        ALL schema tags must match (AND logic). Each tag is matched
        independently against the section's tags.
        """
        for schema_tag in self.tags:
            neg = False
            tag = schema_tag
            if tag.startswith("!"):
                neg = True
                tag = tag[1:].strip()
            matched = match_tag(tag, section.tags)
            if neg:
                matched = not matched
            if not matched:
                return False
        return True

    def validate(self, section: "Section") -> list[str]:
        """
        Validate section against schema definitions.

        TWO SEPARATE VALIDATIONS:
        1. Header properties - always validated against schema
        2. FTML body content - validated if section's content type is 'ftml'

        Both validations use the same schema definitions but are independent.
        The header and body can have different data - both must be valid.

        Returns list of error messages (empty if valid).
        """
        errors = []

        # Validation 1: Header properties
        try:
            params_ftml = self._parameters_to_ftml(section.parameters)
            header_errors = validate_ftml(params_ftml, self.property_definitions)
            for err in header_errors:
                errors.append(f"Header property error: {err}")
        except Exception as e:
            errors.append(f"Header validation error: {str(e)}")

        # Validation 2: FTML body content (only if content type is 'ftml')
        if section.type_name.lower() == "ftml":
            try:
                body_content = section.raw_content
                if body_content.strip():  # Only validate non-empty body
                    body_errors = validate_ftml(body_content, self.property_definitions)
                    for err in body_errors:
                        errors.append(f"Body content error: {err}")
            except Exception as e:
                errors.append(f"Body validation error: {str(e)}")

        return errors

    def _parameters_to_ftml(self, parameters: dict[str, Any]) -> str:
        """
        Convert section parameters dict to FTML format for validation.
        """
        lines = []
        for key, value in parameters.items():
            if isinstance(value, str):
                # Escape quotes in string values
                escaped = value.replace("\\", "\\\\").replace('"', '\\"')
                lines.append(f'{key} = "{escaped}"')
            elif isinstance(value, bool):
                lines.append(f'{key} = {"true" if value else "false"}')
            elif value is None:
                lines.append(f"{key} = null")
            elif isinstance(value, (int, float)):
                lines.append(f"{key} = {value}")
            elif isinstance(value, list):
                # Handle lists - convert to FTML array syntax
                items = []
                for item in value:
                    if isinstance(item, str):
                        escaped = item.replace("\\", "\\\\").replace('"', '\\"')
                        items.append(f'"{escaped}"')
                    elif isinstance(item, bool):
                        items.append("true" if item else "false")
                    elif item is None:
                        items.append("null")
                    else:
                        items.append(str(item))
                lines.append(f'{key} = [{", ".join(items)}]')
            else:
                # Fallback for other types
                lines.append(f"{key} = {value}")
        return "\n".join(lines)


##############################################################################
# FTML AND YAML PARSERS
##############################################################################

try:
    import yaml
except ImportError:
    yaml = None

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

try:
    import ftml
except ImportError:
    ftml = None


def parse_ftml(content: str) -> Any:
    """
    Parse FTML content into Python objects using the actual FTML library.
    """
    if not ftml:
        raise FlexTagSyntaxError(
            "FTML library not installed. Install with: pip install ftml"
        )

    try:
        logger.debug("Parsing content with FTML library")
        # Use the actual FTML parser
        return ftml.load(content)
    except Exception as e:
        raise FlexTagSyntaxError(f"FTML parsing error: {e}")


def parse_yaml(content: str) -> Any:
    """
    Parse YAML content into Python objects.
    """
    if not yaml:
        raise FlexTagSyntaxError(
            "YAML library not installed. Install with: pip install pyyaml"
        )

    try:
        logger.debug("Parsing content with YAML library")
        return yaml.safe_load(content)
    except yaml.YAMLError as e:
        raise FlexTagSyntaxError(f"YAML parsing error: {e}")


def parse_json(content: str) -> Any:
    """
    Parse JSON content into Python objects.
    """
    try:
        logger.debug("Parsing content with JSON library")
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise FlexTagSyntaxError(f"JSON parsing error: {e}")


def parse_toml(content: str) -> Any:
    """
    Parse TOML content into Python objects.
    """
    if not tomllib:
        raise FlexTagSyntaxError(
            "TOML library not available. For Python 3.11+, use built-in tomllib. For earlier versions, install with: pip install tomli"
        )

    try:
        logger.debug("Parsing content with TOML library")
        return tomllib.loads(content)
    except Exception as e:
        raise FlexTagSyntaxError(f"TOML parsing error: {e}")


def validate_ftml(content: str, schema: str) -> list[str]:
    """
    Validate FTML content against the schema using the actual FTML library.
    Takes the raw FTML content string, not parsed data.
    Returns a list of error messages (empty if valid).
    """
    if not ftml:
        logger.warning("FTML library not available, skipping validation")
        return []

    try:
        # Validate the raw FTML content directly against the schema
        logger.debug("Validating FTML content against schema")
        ftml.load(content, schema=schema)
        return []
    except Exception as e:
        logger.debug(f"FTML validation failed: {e}")
        return [str(e)]


def find_comment_position(line: str) -> int:
    """
    Find the position of '//' that indicates a comment start,
    but ignore '//' that appears inside quoted strings.
    Returns -1 if no comment marker is found.
    """
    i = 0
    in_single_quote = False
    in_double_quote = False

    while i < len(line) - 1:  # -1 because we need to check two characters
        char = line[i]

        # Handle escape sequences in double quotes
        if in_double_quote and char == "\\":
            i += 2  # Skip the escaped character
            continue

        # Handle single quote escaping in single quotes ('' becomes ')
        if in_single_quote and char == "'" and i + 1 < len(line) and line[i + 1] == "'":
            i += 2  # Skip the escaped single quote
            continue

        # Toggle quote states
        if char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
        elif char == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
        # Check for comment marker when not in quotes
        elif not in_single_quote and not in_double_quote:
            if line[i : i + 2] == "//":
                return i

        i += 1

    return -1  # No comment found


##############################################################################
# PARSER
##############################################################################
class FlexParser:
    """
    Handles bracket-based parsing for double-bracket sections (user content).
    For single-bracket sections, we do not parse them here; they are for schema lines
    or other advanced usage. The schema logic is handled by ExtendedSchemaParser.
    """

    def __init__(self):
        pass

    def parse_bracket_sections(
        self, lines: list[str], source_name: str
    ) -> list[dict[str, Any]]:
        """
        Enhanced version that correctly handles 'file-metadata' sections and extracts their metadata.
        """
        open_pat_str = r"^\s*\[\[\s*(.*?)\]\]\s*(?::\s*(.*?))?$"
        close_pat_str = r"^\s*\[\[/\s*\]\]\s*$"  # Just [[/]] - no ID needed
        open_pat = re.compile(open_pat_str)
        close_pat = re.compile(close_pat_str)

        sections = []
        i = 0
        n = len(lines)

        while i < n:
            line = lines[i].rstrip("\n")

            if not line.strip() or line.strip().startswith("#"):
                i += 1
                continue

            m_open = open_pat.match(line)
            if m_open:
                bracket_str = m_open.group(1) or ""
                type_decl = m_open.group(2) or ""

                # Check for multiple type declarations
                if type_decl and ":" in type_decl:
                    # Find the position of the second colon directly
                    first_colon_pos = line.find(":")
                    second_colon_pos = line.find(":", first_colon_pos + 1)

                    raise FlexTagSyntaxError(
                        "Multiple type declarations",
                        line_num=i + 1,
                        column_num=second_colon_pos + 1,
                        source_name=source_name,
                        line_content=line,
                    )

                open_line = i
                bracket_str = m_open.group(1) or ""
                type_decl = m_open.group(2) or ""
                section_id, tags, params, is_self_closing = (
                    self._interpret_open_bracket(bracket_str, source_name, i + 1)
                )

                close_line = open_line
                raw_content = ""
                i += 1

                if not is_self_closing:
                    content_lines = []
                    found_close = False
                    while i < n:
                        c_line = lines[i].rstrip("\n")
                        m_close = close_pat.match(c_line)
                        if m_close:
                            found_close = True
                            close_line = i
                            i += 1
                            break
                        else:
                            content_lines.append(lines[i])
                            i += 1
                    if not found_close:
                        raise FlexTagSyntaxError(
                            "No matching close tag [[/]] found",
                            line_num=n,
                            source_name=source_name,
                        )

                    raw_content = "".join(content_lines)
                    if raw_content.endswith("\n"):
                        raw_content = raw_content[:-1]

                section_data = {
                    "section_id": section_id,
                    "tags": tags,
                    "params": params,
                    "open_line": open_line,
                    "close_line": close_line,
                    "is_self_closing": is_self_closing,
                    "type_decl": type_decl,
                    "raw_content": raw_content,
                }

                sections.append(section_data)
            else:
                # Check if this is a non-empty line that's not a comment
                if line.strip() and not line.strip().startswith("#"):
                    raise FlexTagSyntaxError(
                        "Lines between sections must be comments starting with #",
                        line_num=i + 1,
                        column_num=1,
                        source_name=source_name,
                        line_content=line,
                    )
                i += 1

        return {
            "sections": sections,
        }

    def _interpret_open_bracket(
        self, bracket_str: str, source_name: str, line_num: int
    ):
        """
        Updated version that uses `shlex.split` to correctly handle
        parameters with quoted strings, e.g. key="some value".
        Now also supports explicit type annotations with colon syntax: key:type=value
        """
        bracket_str = bracket_str.strip()
        is_self_closing = False

        # Check for trailing '/' to mark self-closing
        if bracket_str.endswith("/"):
            bracket_str = bracket_str[:-1].rstrip()
            is_self_closing = True

        # Use shlex to properly split on spaces while respecting quotes
        try:
            tokens = shlex.split(bracket_str)
        except ValueError as e:
            raise FlexTagSyntaxError(
                f"Error parsing bracket metadata: {e}",
                line_num=line_num,
                source_name=source_name,
            )

        # IDs are no longer used - sections are identified by tags/parameters
        section_id = ""
        tags = []
        params = {}

        # Parse all tokens as #tag or key=value (@ is legacy, converted to #)
        for t in tokens:
            if t.startswith("#") or t.startswith("!#"):
                tags.append(t)
            elif t.startswith("@"):
                # Legacy @ prefix - convert to #tag
                tags.append("#" + t[1:])
            elif "=" in t:
                k, v = t.split("=", 1)
                k = k.strip()

                # Check for explicit type annotation
                if ":" in k:
                    key, type_name = k.split(":", 1)
                    key = key.strip()
                    type_name = type_name.strip().lower()

                    # Convert value based on an explicit type
                    val = self._convert_value_by_type(v, type_name)
                    params[key] = val
                else:
                    # No explicit type, use automatic inference
                    val = parse_basic_value(v)
                    params[k] = val
            else:
                # Invalid token - neither a tag nor key=value parameter
                # This might be someone trying to use an ID (no longer supported)
                raise FlexTagSyntaxError(
                    f"Invalid token '{t}' in bracket. Use #tag for tags "
                    f"or key=value for parameters. Section IDs are no longer supported.",
                    line_num=line_num,
                    source_name=source_name,
                )

        return section_id, tags, params, is_self_closing

    def _convert_value_by_type(self, value_str: str, type_name: str):
        """
        Convert a string value to the specified type.
        Supports: str, int, float, bool, null
        Falls back to parse_basic_value for unknown types.
        """
        value_str = value_str.strip()

        # Handle nullable types (type?)
        is_nullable = type_name.endswith("?")
        if is_nullable:
            type_name = type_name[:-1].strip()
            if value_str.lower() == "null":
                return None

        if type_name in ("str", "string"):
            # Remove quotes if present
            if value_str.startswith('"') and value_str.endswith('"'):
                return value_str[1:-1]
            return value_str
        elif type_name in ("int", "integer"):
            try:
                return int(value_str)
            except ValueError:
                raise FlexTagSyntaxError(f"Cannot convert '{value_str}' to int")
        elif type_name == "float":
            try:
                return float(value_str)
            except ValueError:
                raise FlexTagSyntaxError(f"Cannot convert '{value_str}' to float")
        elif type_name == "bool":
            lower_val = value_str.lower()
            if lower_val == "true":
                return True
            elif lower_val == "false":
                return False
            else:
                raise FlexTagSyntaxError(
                    f"Boolean value must be 'true' or 'false', got '{value_str}'"
                )
        elif type_name == "null":
            if value_str.lower() == "null":
                return None
            else:
                raise FlexTagSyntaxError(
                    f"Null value must be 'null', got '{value_str}'"
                )
        else:
            # Unknown type, fall back to automatic inference
            logger.warning(
                f"Unknown type '{type_name}', using automatic type inference"
            )
            return parse_basic_value(value_str)


##############################################################################
# SECTION
##############################################################################
class Section:
    """
    Represents a single bracketed block of content.
    Type can be 'raw' (default), 'ftml', or any registered parser.
    """

    def __init__(
        self,
        section_id: str,
        tags: list[str],
        parameters: dict[str, Any],
        type_name: str,
        open_line: int,
        close_line: int,
        is_self_closing: bool,
        all_lines: list[str],
        source_name: str = "",
    ):
        self.raw_id = section_id
        self.raw_tags = tags[:]
        self.raw_parameters = dict(parameters)
        self.raw_type_name = (
            type_name.strip() if type_name else "text"
        )  # Default to 'text'
        self.open_line = open_line
        self.close_line = close_line
        self.is_self_closing = is_self_closing
        self._all_lines = all_lines
        self._parsed_cache = None

        self.source_name = source_name
        self.inherited_id: str | None = None
        self.inherited_tags: list[str] = []
        self.inherited_params: dict[str, Any] = {}
        self.inherited_type: str | None = None

    def __repr__(self):
        return f"<Section ID={self.id!r} type={self.type_name!r}>"

    @property
    def id(self) -> str:
        if self.raw_id:
            return self.raw_id
        return self.inherited_id or ""

    @property
    def tags(self) -> list[str]:
        out = list(self.inherited_tags)
        for p in self.raw_tags:
            if p not in out:
                out.append(p)
        return out

    @property
    def parameters(self) -> dict[str, Any]:
        out = dict(self.inherited_params)
        out.update(self.raw_parameters)
        return out

    @property
    def type_name(self) -> str:
        if (
            not self.raw_type_name or self.raw_type_name == "text"
        ) and self.inherited_type:
            return self.inherited_type
        return self.raw_type_name

    @property
    def raw_content(self) -> str:
        if self.is_self_closing:
            return ""
        if self.close_line <= self.open_line:
            return ""
        raw = "".join(self._all_lines[self.open_line + 1 : self.close_line])
        if raw.endswith("\n"):
            return raw[:-1]
        return raw

    @property
    def content(self) -> Any:
        if self._parsed_cache is None:
            self._parsed_cache = self._parse_content()
        return self._parsed_cache

    def _parse_content(self) -> Any:
        """
        Parse content based on type_name: 'text', 'binary', 'ftml', 'yaml', 'json', 'toml', etc.
        'file-metadata', 'defaults', 'schema' handle separately in Container.
        """
        raw = self.raw_content
        tname = self.type_name.lower().strip()

        # If no content, return empty string
        if not raw:
            return ""

        # Handle basic content types
        if tname == "text" or tname == "":
            # Text content - return as-is
            logger.debug(f"Parsing section ID='{self.id}' as text.")
            return raw

        elif tname == "binary":
            # Binary content - convert to bytes using surrogateescape
            logger.debug(f"Parsing section ID='{self.id}' as binary.")
            return raw.encode("utf-8", errors="surrogateescape")

        # Handle markup content types
        elif tname == "ftml":
            # Parse with FTML library
            try:
                logger.debug(f"Parsing section ID='{self.id}' as FTML.")
                return parse_ftml(raw)
            except Exception as e:
                raise FlexTagSyntaxError(
                    f"FTML parsing error in section '{self.id}': {e}"
                )

        elif tname == "ftml-schema":
            # Schema sections store raw FTML schema content
            # They are processed specially during Container initialization
            # Return raw content - it will be used by PropertySchema for validation
            logger.debug(f"Section ID='{self.id}' is an ftml-schema section.")
            return raw

        elif tname == "yaml":
            # Parse with YAML library
            try:
                logger.debug(f"Parsing section ID='{self.id}' as YAML.")
                return parse_yaml(raw)
            except Exception as e:
                raise FlexTagSyntaxError(
                    f"YAML parsing error in section '{self.id}': {e}"
                )

        elif tname == "json":
            # Parse with JSON library
            try:
                logger.debug(f"Parsing section ID='{self.id}' as JSON.")
                return parse_json(raw)
            except Exception as e:
                raise FlexTagSyntaxError(
                    f"JSON parsing error in section '{self.id}': {e}"
                )

        elif tname == "toml":
            # Parse with TOML library
            try:
                logger.debug(f"Parsing section ID='{self.id}' as TOML.")
                return parse_toml(raw)
            except Exception as e:
                raise FlexTagSyntaxError(
                    f"TOML parsing error in section '{self.id}': {e}"
                )

        # file-metadata sections use header tags/params only, no body parsing needed
        elif tname == "file-metadata":
            return raw

        # Default: treat unknown types as text with a warning
        else:
            logger.warning(
                f"Unknown content type '{tname}' in section '{self.id}', treating as text."
            )
            return raw


##############################################################################
# CONTAINER
##############################################################################
class Container:
    """
    Holds sections from a single flextag source.
    File-level metadata comes from file-metadata sections.
    Schema validation uses ftml-schema sections.
    """

    def __init__(
        self,
        sections: list[Section],
        source_name: str,
    ):
        self.source_name = source_name
        self.raw_sections = sections[:]
        self.sections: list[Section] = []
        self.file_metadata: Section | None = None
        self.defaults: Section | None = None

        self.id: str = ""
        self.tags: list[str] = []
        self.parameters: dict[str, Any] = {}

        for sec in self.raw_sections:
            stype = sec.type_name.lower()
            if stype == "file-metadata":
                self.file_metadata = sec
            elif stype == "defaults":
                self.defaults = sec
            else:
                self.sections.append(sec)

        # Promote file-metadata header tags/params to the Container level
        if self.file_metadata:
            self.tags = list(self.file_metadata.tags)
            self.parameters = dict(self.file_metadata.parameters)

        if self.defaults:
            self._apply_defaults()

        # Collect property schemas from ftml-schema sections
        self._collect_property_schemas()

    def _apply_defaults(self):
        if not self.defaults:
            return  # No defaults section at all

        logger.debug("Applying bracket-based default metadata.")

        d_id, d_tags, d_params = _parse_defaults_block(self.defaults)
        logger.debug(f"Default tags: {d_tags}")

        if not (d_id or d_tags or d_params):
            logger.debug("No bracket block found in defaults. Skipping.")
            return

        # Merge these defaults into all user sections
        for s in self.sections:
            logger.debug(
                f"Section before: id={s.id}, tags={s.tags}, inherited_tags={s.inherited_tags}"
            )

            if d_id and not s.inherited_id:
                s.inherited_id = d_id

            # Add default tags to inherited_tags
            s.inherited_tags = list(s.inherited_tags)  # Make a copy
            s.inherited_tags.extend(d_tags)  # Add all default tags

            # Merge params: defaults first, then existing
            merged = dict(d_params)
            merged.update(s.inherited_params)
            s.inherited_params = merged

            logger.debug(
                f"Section after: id={s.id}, tags={s.tags}, inherited_tags={s.inherited_tags}"
            )

    def validate_schema(self):
        """
        Validate header properties of sections against matching property schemas.

        Schema matching is tag-based:
        - A schema applies to a section if the section's tags CONTAIN all of the schema's tags
        - Multiple schemas can match one section (all are applied)
        - Nested tag inheritance: #schema.product.laptop matches #schema.product schema
        """
        if hasattr(self, "property_schemas") and self.property_schemas:
            logger.debug(
                f"Validating with {len(self.property_schemas)} property schemas."
            )
            self._validate_property_schemas()
        else:
            logger.debug("No property schemas present. Skipping validation.")

    # =========================================================================
    # NEW PROPERTY SCHEMA SYSTEM (tag-based, header property validation)
    # =========================================================================

    def _collect_property_schemas(self):
        """
        Collect all PropertySchema definitions from ftml-schema sections.

        Schema tags use the same syntax as filter queries:
          [[#adapter]]: ftml-schema    — exact match only
          [[#adapter*]]: ftml-schema   — self + all descendants
          [[#adapter+]]: ftml-schema   — immediate children only
        """
        self.property_schemas: list[PropertySchema] = []

        # Find all ftml-schema sections
        for section in self.raw_sections:
            if section.type_name.lower() == "ftml-schema":
                schema = PropertySchema(
                    tags=section.tags,
                    property_definitions=section.raw_content,
                    source_section=section,
                )
                self.property_schemas.append(schema)
                logger.debug(f"Collected property schema: {schema}")

    def _find_matching_schemas(self, section: Section) -> list[PropertySchema]:
        """
        Find all property schemas that apply to the given section.
        Returns list of matching schemas (can be multiple).
        """
        if not hasattr(self, "property_schemas"):
            return []
        return [s for s in self.property_schemas if s.matches_section(section)]

    def _validate_property_schemas(self):
        """
        Validate sections against matching property schemas.

        Schema tags use the same syntax as filter queries (#tag, #tag*, #tag+).
        Multiple schemas can match one section — all are applied.
        """
        if not hasattr(self, "property_schemas") or not self.property_schemas:
            logger.debug("No property schemas present. Skipping validation.")
            return

        for section in self.sections:
            # Skip schema sections themselves
            if section.type_name.lower() == "ftml-schema":
                continue

            matching_schemas = self._find_matching_schemas(section)
            for schema in matching_schemas:
                errors = schema.validate(section)
                if errors:
                    error_msg = "\n".join(errors)
                    raise SchemaValidationError(
                        f"Schema validation errors for section at line {section.open_line}:\n{error_msg}",
                        source_file=self.source_name,
                        line_num=section.open_line,
                    )


##############################################################################
# COLLECTION CLASSES
##############################################################################


class SectionCollection:
    """
    Wraps a list of Section objects, giving them .help, etc.
    """

    def __init__(self, sections: list[Section]):
        self._sections = sections

    def __len__(self):
        return len(self._sections)

    def __getitem__(self, idx):
        return self._sections[idx]

    def __iter__(self):
        return iter(self._sections)


class ContainerCollection:
    """
    Wraps a list of Container objects, allowing iteration and .help if needed.
    """

    def __init__(self, containers: list[Container]):
        self._containers = containers

    def __len__(self):
        return len(self._containers)

    def __getitem__(self, idx):
        return self._containers[idx]

    def __iter__(self):
        return iter(self._containers)


##############################################################################
# FLEX VIEW
##############################################################################


class FlexView:
    """
    Top-level container for multiple Container objects.
    Provides filtering and section access capabilities.
    """

    def __init__(self, containers: list[Container]):
        self._containers = containers
        self._raw_sections: list[Section] = []
        self._user_sections: list[Section] = []

        for c in containers:
            self._raw_sections.extend(c.raw_sections)
            self._user_sections.extend(c.sections)

    @property
    def containers(self) -> ContainerCollection:
        return ContainerCollection(self._containers)

    @property
    def sections(self) -> SectionCollection:
        return SectionCollection(self._user_sections)

    @property
    def raw_sections(self) -> SectionCollection:
        return SectionCollection(self._raw_sections)

    def filter(self, query: str, target: str = "sections") -> "FlexView":
        """
        Provide a param/tag-based filter for sections or containers.
        """
        logger.debug(f"Filtering with query='{query}', target='{target}'.")
        or_split = re.compile(r"\s+(?i:OR)\s+")
        parts = or_split.split(query.strip())
        ast = []
        for p in parts:
            tokens = p.split()
            if tokens:
                ast.append(tokens)

        if target.lower() == "sections":
            matched_secs = []
            for s in self._raw_sections:
                if self._match_section(s, ast):
                    matched_secs.append(s)
            new_conts = []
            for c in self._containers:
                sub_secs = [sec for sec in c.sections if sec in matched_secs]
                if sub_secs:
                    new_c = Container(sub_secs, c.source_name)
                    # preserve file metadata and special sections
                    new_c.file_metadata = c.file_metadata
                    new_c.defaults = c.defaults
                    new_c.id = c.id
                    new_c.tags = c.tags.copy()
                    new_c.parameters = c.parameters.copy()
                    # preserve property schemas
                    if hasattr(c, "property_schemas"):
                        new_c.property_schemas = c.property_schemas
                    new_conts.append(new_c)
            return FlexView(new_conts)

        elif target.lower() == "containers":
            matched_conts = []
            for c in self._containers:
                # For debugging
                logger.debug(
                    f"Container ID: {c.id}, Tags: {c.tags}, Params: {c.parameters}"
                )

                for subexpr in ast:  # OR
                    all_tokens_match = True
                    for tok in subexpr:  # AND
                        if not self._match_container_token(tok, c):
                            all_tokens_match = False
                            break

                    if all_tokens_match:
                        matched_conts.append(c)
                        break

            return FlexView(matched_conts)

        else:
            logger.warning(f"Unknown filter target={target}, ignoring filter")
            return self

    def _match_container_token(self, token: str, container) -> bool:
        """
        Match a single token against container metadata.
        Handles tags (#tag), parameter expressions, and ID matching.
        """
        neg = False
        if token.startswith("!"):
            neg = True
            token = token[1:].strip()

        matched = False

        # Legacy @ prefix - convert to # for matching
        if token.startswith("@"):
            token = "#" + token[1:]

        # Handle tag match using shared match_tag logic
        if token.startswith("#"):
            matched = match_tag(token, container.tags)

        # Handle parameter expression (key=value, key>=value, etc.)
        elif OP_PATTERN.match(token):
            m = OP_PATTERN.match(token)
            key, op, rhs_str = (
                m.group(1).strip(),
                m.group(2).strip(),
                m.group(3).strip(),
            )

            # Debug output
            logger.debug(
                f"Parameter expression: key='{key}', op='{op}', rhs_str='{rhs_str}'"
            )

            if key in container.parameters:
                lhs_val = container.parameters[key]

                # Handle quoted strings specially - remove quotes if present
                if (
                    rhs_str.startswith('"')
                    and rhs_str.endswith('"')
                    and len(rhs_str) >= 2
                ):
                    rhs_str = rhs_str[1:-1]  # Remove surrounding quotes

                # Convert to appropriate type
                rhs_val = parse_basic_value(rhs_str)

                logger.debug(f"Comparing: '{lhs_val}' {op} '{rhs_val}'")
                matched = compare_op(lhs_val, rhs_val, op)
                logger.debug(f"Match result: {matched}")
            else:
                logger.debug(
                    f"Parameter '{key}' not found in container with params: {container.parameters}"
                )

        # Handle ID match
        else:
            matched = token == container.id

        return (not matched) if neg else matched

    def _match_section(self, sec, ast_list):
        for subexpr in ast_list:  # OR
            if all(self._match_token(tok, sec) for tok in subexpr):  # AND
                return True
        return False

    def _match_token(self, token: str, sec: Section) -> bool:
        neg = False
        if token.startswith("!"):
            neg = True
            token = token[1:].strip()
        matched = self._match_token_core(token, sec)
        return (not matched) if neg else matched

    def _match_token_core(self, token: str, sec: Section) -> bool:
        # Legacy @ prefix - convert to # for matching
        if token.startswith("@"):
            token = "#" + token[1:]

        # Legacy . prefix - convert to # for matching
        if token.startswith("."):
            token = "#" + token[1:]

        # Handle tag match using shared match_tag logic
        if token.startswith("#"):
            return match_tag(token, sec.tags)

        # If param expression
        m = OP_PATTERN.match(token)
        if m:
            key, op, rhs_str = (
                m.group(1).strip(),
                m.group(2).strip(),
                m.group(3).strip(),
            )
            if key not in sec.parameters:
                return False
            lhs_val = sec.parameters[key]
            rhs_val = parse_basic_value(rhs_str)
            return compare_op(lhs_val, rhs_val, op)

        # else match by ID
        return token == sec.id


##############################################################################
# FLEXTAG
##############################################################################


class FlexTag:
    """
    Main entry point for loading .flextag or .ft files or raw strings.
    """

    def __init__(self, settings: FlexTagSettings | None = None):
        self._parser = FlexParser()
        self.settings = settings if settings else FlexTagSettings()

    @classmethod
    def load(
        cls,
        path: str | list[str] | None = None,
        string: str | list[str] | None = None,
        dir: str | list[str] | None = None,
        filter_query: str | None = None,
        validate: bool = True,
        settings: FlexTagSettings | None = None,
        recursive: bool = True,
    ) -> FlexView:
        inst = cls(settings=settings)
        sources = inst._gather_sources(path, string, dir, recursive)
        containers = []
        for src in sources:
            src_path = src if os.path.isfile(src) else "<string>"
            c = inst._parse_source(src, src_path)
            if validate:
                c.validate_schema()
            containers.append(c)
        view = FlexView(containers)
        if filter_query:
            return view.filter(filter_query, target="containers")
        return view

    def _gather_sources(
        self,
        path: str | list[str] | None,
        string: str | list[str] | None,
        dir: str | list[str] | None,
        recursive: bool = True,
    ) -> list[str]:
        out = []
        if path:
            if isinstance(path, str):
                out.append(path)
            else:
                out.extend(path)
        if string:
            if isinstance(string, str):
                out.append(string)
            else:
                out.extend(string)
        if dir:
            if isinstance(dir, str):
                out.extend(self._dir_files(dir, recursive))
            else:
                for d in dir:
                    out.extend(self._dir_files(d, recursive))
        return out

    def _dir_files(self, directory: str, recursive: bool = True) -> list[str]:
        res = []
        if not os.path.isdir(directory):
            return res
        if recursive:
            for root, _, files in os.walk(directory):
                for fn in files:
                    if fn.endswith(".flextag") or fn.endswith(".ft"):
                        res.append(os.path.join(root, fn))
        else:
            for fn in os.listdir(directory):
                if fn.endswith(".flextag") or fn.endswith(".ft"):
                    res.append(os.path.join(directory, fn))
        return res

    def _parse_source(self, src: str, source_name: str) -> Container:
        if os.path.exists(src) and os.path.isfile(src):
            logger.debug(f"Parsing file: {src}")
            with open(src, encoding="utf-8", errors="surrogateescape") as f:
                lines = f.readlines()
        else:
            logger.debug("Parsing raw string input.")
            lines = src.splitlines(keepends=True)

        parse_result = self._parser.parse_bracket_sections(lines, source_name)
        raw_secs = parse_result["sections"]

        sections = []
        for rs in raw_secs:
            s_obj = Section(
                section_id=rs["section_id"],
                tags=rs["tags"],
                parameters=rs["params"],
                type_name=rs["type_decl"],
                open_line=rs["open_line"],
                close_line=rs["close_line"],
                is_self_closing=rs["is_self_closing"],
                all_lines=lines,
                source_name=source_name,
            )
            sections.append(s_obj)

        container = Container(sections, source_name)
        return container


if __name__ == "__main__":
    # Simple usage example with new syntax
    example = r"""
[[#file_tag debug=true]]: file-metadata
[[/]]

[[#text]]
text
[[/]]

[[#items]]: ftml
[
  "apple",
  "banana",
  "orange"
]
[[/]]

[[#items]]: ftml
[
  "apple2",
  "banana2",
  "orange2"
]
[[/]]

[[#notes #draft #research]]
This is a text block by default
[[/]]

[[#text]]
text 2
[[/]]
"""
    view = FlexTag.load(string=example, validate=False)
    for section in view.sections:
        print(f"Tags: {section.tags}, Content: {section.content[:50]}...")
