import collections
import json
import os
import re
import shlex
import logging
from collections import deque
from typing import (
    List,
    Dict,
    Any,
    Union,
    Optional,
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
# PARSING HELPERS
##############################################################################

OP_PATTERN = re.compile(r"^([^=!<>]+)\s*(=|!=|>=|<=|>|<)\s*(.+)$")


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
    lines: List[str],
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
    paths = []
    params = {}

    # Special handling for '[' as a separate token
    if tokens and tokens[0] == "[":
        tokens = tokens[1:]  # Skip the opening bracket token

    if tokens:
        first = tokens[0]
        if first.startswith("[#"):
            # Extract the tag part and add it to tags
            tags.append("#" + first[2:])
            tokens = tokens[1:]
        elif first.startswith("[@"):
            # Extract the path part and add it to paths
            paths.append("@" + first[2:])
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
        if t.startswith("#"):
            tags.append(t)
        elif t.startswith("@"):
            paths.append(t)
        elif t.startswith("."):
            # Deprecated path syntax
            logger.warning(
                f"Deprecated path syntax '.{t[1:]}' used. "
                f"Please use '@{t[1:]}' instead."
            )
            # Convert to new syntax internally
            paths.append("@" + t[1:])
        elif "=" in t:
            k, v = t.split("=", 1)
            params[k.strip()] = parse_basic_value(v)
        else:
            # Bare token => param=True
            params[t] = True

    logger.debug(f"Default tags: {tags}")
    logger.debug(f"Default paths: {paths}")
    logger.debug(f"Default params: {params}")
    return (section_id, tags, paths, params, is_self_closing)


def _parse_defaults_block(defaults_section) -> (str, list, list, dict):
    """
    Finds the first bracket block [ ... ] in the defaults section's content
    (which may span multiple lines). Returns (d_id, d_tags, d_paths, d_params).
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
        return "", [], [], {}

    # Now parse that bracket string with your standard method:
    d_id, tags, paths, params, _ = _interpret_bracket_meta(
        bracket_str,
        line_num=i,  # Use the index we saved
        source_name=defaults_section.source_name,
        original_line=original_line,  # Use the saved original line
    )
    return d_id, tags, paths, params


##############################################################################
# SCHEMA RULES
##############################################################################
class SchemaRule:
    """
    Stores info about one section rule:
      - section_id
      - required tags, paths, params
      - type_name: "raw", "ftml", etc.
      - repetition: '?', '*', '+', or none
      - content_fields: an extended dict describing each field if ftml
    """

    def __init__(
        self,
        section_id: str,
        tags: List[str],
        paths: List[str],
        parameters: Dict[str, Any],
        type_name: str,
        repetition_symbol: Optional[str] = None,
    ):
        self.section_id = section_id
        self.tags = tags
        self.paths = paths
        self.parameters = parameters
        self.type_name = type_name.lower() if type_name else "raw"
        self.repetition_symbol = repetition_symbol  # '?' | '*' | '+' | None

        # For FTML content constraints, you can store structured fields here
        self.ftml_fields = {}  # "field_name" -> (field_config)

    def __repr__(self):
        return (
            f"<SchemaRule id={self.section_id!r} type={self.type_name!r} "
            f"repetition={self.repetition_symbol!r} tags={self.tags}>"
        )


##############################################################################
# SCHEMA EXTENDED PARSER
##############################################################################


class ExtendedSchemaParser:
    """
    Pre-parses lines in the [schema] block, building a list of SchemaRule objects.
    Each line might look like:

      [id #tag @path key="value"]+: ftml
        fieldA: !!str
        fieldB?: !!int? = 10
        ...

    We'll parse it line by line, detect repetition symbols,
    plus we can parse the nested lines if it's a 'ftml' content field definition block.
    """

    # Regex to capture something like "[id @path #tag key=val]?: typeName"
    # group(1) => "id @path #tag key=val"
    # group(2) => repetition symbol (?), +, or *
    # group(3) => typeName (optional)
    SCHEMA_LINE_RE = re.compile(r"^\s*\[([^\]]+)\](?:(\?|\+|\*)\s*)?:\s*(\S+)\s*$")

    def __init__(self, source_name: str):
        self.source_name = source_name

    def parse_schema_block(self, lines: List[str]) -> List[SchemaRule]:
        """
        Parse lines from the schema section,
        building a list of SchemaRule objects, each describing
        a single bracketed rule line.
        """
        rules = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            line_idx = i  # Save original index before incrementing
            i += 1
            if not line or line.startswith("#"):
                continue

            # we can detect bracket lines with regex
            m = self.SCHEMA_LINE_RE.match(line)
            if m:
                bracket_str = m.group(1)  # e.g. "id #tag @path key=val /"
                repetition_symbol = m.group(2)  # ? + *
                type_decl = m.group(3)  # "ftml" or "raw"

                # parse bracket metadata
                sec_id, sec_tags, sec_paths, sec_params, is_self_closing = (
                    _interpret_bracket_meta(
                        bracket_str,
                        line_num=line_idx + 1,  # Adjust for 1-based line numbering
                        source_name=self.source_name,  # Use the source_name from the parser
                        original_line=line,  # Use the current line
                    )
                )

                # create rule
                rule = SchemaRule(
                    section_id=sec_id,
                    tags=sec_tags,
                    paths=sec_paths,
                    parameters=sec_params,
                    type_name=type_decl,
                    repetition_symbol=repetition_symbol,
                )
                rules.append(rule)

            else:
                # Possibly parse sub-fields if you want lines like "field: !!int"
                # We skip them here. Or do an advanced approach.
                pass

        return rules


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


def validate_ftml(content: str, schema: str) -> List[str]:
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
        logger.debug(f"Validating FTML content against schema")
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
        self, lines: List[str], source_name: str
    ) -> List[Dict[str, Any]]:
        """
        Enhanced version that correctly handles 'container' sections and extracts their metadata.
        """
        open_pat_str = r"^\s*\[\[\s*(.*?)\]\]\s*(?::\s*(.*?))?$"
        close_pat_str = r"^\s*\[\[/\s*(.*?)\]\]\s*$"
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
                is_container = (
                    type_decl.lower() == "container"
                )  # Identify container sections

                section_id, tags, paths, params, is_self_closing = (
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
                            found_id = m_close.group(1).strip()
                            if found_id.lower() == section_id.lower():
                                found_close = True
                                close_line = i
                                i += 1
                                break
                            else:
                                raise FlexTagSyntaxError(
                                    f"Mismatched close ID='{found_id}', expected='{section_id}'",
                                    line_num=i + 1,
                                    source_name=source_name,
                                )
                        else:
                            content_lines.append(lines[i])
                            i += 1
                    if not found_close:
                        raise FlexTagSyntaxError(
                            f"No matching close for ID='{section_id}'",
                            line_num=n,
                            source_name=source_name,
                        )

                    raw_content = "".join(content_lines)
                    if raw_content.endswith("\n"):
                        raw_content = raw_content[:-1]

                section_data = {
                    "section_id": section_id,
                    "tags": tags,
                    "paths": paths,
                    "params": params,
                    "open_line": open_line,
                    "close_line": close_line,
                    "is_self_closing": is_self_closing,
                    "type_decl": type_decl,
                    "raw_content": raw_content,
                }

                if is_container:
                    # If it's a container, parse its content for metadata
                    section_data["container_metadata"] = self._parse_container_metadata(
                        raw_content
                    )
                else:
                    section_data["container_metadata"] = (
                        None  # Ensure it's always present
                    )

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

        return sections  # Return after processing ALL sections, not just the first one

    def _parse_container_metadata(self, raw_content: str) -> Dict[str, Any]:
        """
        Parses the raw content of a container section to extract metadata.
        This assumes a simple key=value format within the container.
        You might need to adjust this based on your exact metadata format.
        """
        metadata = {}
        for line in raw_content.splitlines():
            line = line.strip()
            if not line:
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                metadata[key.strip()] = parse_basic_value(value.strip())
        return metadata

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

        section_id = ""
        tags = []
        paths = []
        params = {}

        # If the first token looks like a bare ID (i.e., it doesn't start with # or . or contain '='),
        # treat that as the section ID.
        if tokens:
            first = tokens[0]
            if (
                not first.startswith("#")
                and not first.startswith("@")
                and "=" not in first
            ):
                section_id = first
                tokens = tokens[1:]

        # Now parse the remaining tokens as #tag, .path, or key=value
        for t in tokens:
            if t.startswith("#"):
                tags.append(t)
            elif t.startswith("@"):
                paths.append(t)
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
                # Invalid token - neither a tag, path, nor key=value parameter
                raise FlexTagSyntaxError(
                    f"Invalid token '{t}' in bracket. Parameters must use key=value format.",
                    line_num=line_num,
                    source_name=source_name,
                )

        return section_id, tags, paths, params, is_self_closing

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
        tags: List[str],
        paths: List[str],
        parameters: Dict[str, Any],
        type_name: str,
        open_line: int,
        close_line: int,
        is_self_closing: bool,
        all_lines: List[str],
        source_name: str = "",
    ):
        self.raw_id = section_id
        self.raw_tags = tags[:]
        self.raw_paths = paths[:]
        self.raw_parameters = dict(parameters)
        self.raw_type_name = (
            type_name.strip() if type_name else "raw"
        )  # Default to 'raw' instead of 'yaml'
        self.open_line = open_line
        self.close_line = close_line
        self.is_self_closing = is_self_closing
        self._all_lines = all_lines
        self._parsed_cache = None

        self.source_name = source_name
        self.inherited_id: Optional[str] = None
        self.inherited_tags: List[str] = []
        self.inherited_paths: List[str] = []
        self.inherited_params: Dict[str, Any] = {}
        self.inherited_type: Optional[str] = None

    def __repr__(self):
        return f"<Section ID={self.id!r} type={self.type_name!r}>"

    @property
    def id(self) -> str:
        if self.raw_id:
            return self.raw_id
        return self.inherited_id or ""

    @property
    def tags(self) -> List[str]:
        out = list(self.inherited_tags)
        for t in self.raw_tags:
            if t not in out:
                out.append(t)
        return out

    @property
    def paths(self) -> List[str]:
        out = list(self.inherited_paths)
        for p in self.raw_paths:
            if p not in out:
                out.append(p)
        return out

    @property
    def parameters(self) -> Dict[str, Any]:
        out = dict(self.inherited_params)
        out.update(self.raw_parameters)
        return out

    @property
    def type_name(self) -> str:
        if (
            not self.raw_type_name or self.raw_type_name == "raw"
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
        Parse content based on type_name: 'raw', 'ftml', 'yaml', 'json', 'toml', etc.
        'container', 'defaults', 'schema' handle separately in Container.
        """
        raw = self.raw_content
        tname = self.type_name.lower().strip()

        # If no content, return empty string
        if not raw:
            return ""

        # Handle different content types
        if tname == "raw" or tname == "":
            # Raw content - return as-is
            logger.debug(f"Parsing section ID='{self.id}' as raw text.")
            return raw

        elif tname == "ftml":
            # Parse with FTML library
            try:
                logger.debug(f"Parsing section ID='{self.id}' as FTML.")
                return parse_ftml(raw)
            except Exception as e:
                raise FlexTagSyntaxError(
                    f"FTML parsing error in section '{self.id}': {e}"
                )

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

        # Handle container type properly
        elif tname == "container":
            # For container type, return lines for Container to process
            return raw.splitlines()

        # Default: treat unknown types as raw content with a warning
        else:
            logger.warning(
                f"Unknown content type '{tname}' in section '{self.id}', treating as raw."
            )
            return raw


##############################################################################
# CONTAINER
##############################################################################
class Container:
    """
    Holds sections from a single flextag source.
    Head sections: 'container', 'defaults', 'schema'.
    All other sections: user sections.
    """

    def __init__(self, sections: List[Section], source_name: str):
        self.source_name = source_name
        self.raw_sections = sections[:]
        self.sections: List[Section] = []
        self.container_metadata: Optional[Section] = None
        self.defaults: Optional[Section] = None
        self.schema: Optional[Section] = None
        self.schema_rules: List[SchemaRule] = []
        self.ftml_schema: Dict[str, Any] = {}  # New: holds parsed FTML schema

        self.id: str = ""
        self.tags: List[str] = []
        self.paths: List[str] = []
        self.parameters: Dict[str, Any] = {}

        for sec in self.raw_sections:
            stype = sec.type_name.lower()
            if stype == "container":
                self.container_metadata = sec
            elif stype == "defaults":
                self.defaults = sec
            elif stype == "schema":
                self.schema = sec
            else:
                self.sections.append(sec)

        if self.container_metadata:
            self._extract_container_metadata()
        if self.defaults:
            self._apply_defaults()

        if self.schema:
            # Parse schema
            self._parse_schema()

    def _extract_container_metadata(self):
        """
        Parse lines from container_metadata as simple key=val or param tokens.
        """
        logger.debug("Extracting container metadata.")

        # Handle both cases: content as string or as list
        if isinstance(self.container_metadata.content, str):
            lines = self.container_metadata.content.splitlines()
        else:
            # Content is already a list of lines
            lines = self.container_metadata.content

        for line in lines:
            ln = line.strip()
            if not ln:
                continue

            # Handle square-bracketed content format: [container_id #tag param="value"]
            if ln.startswith("[") and ln.endswith("]"):
                ln = ln[1:-1].strip()  # Remove the square brackets

            c_id, c_tags, c_paths, c_params = self._parse_head_metadata_line(ln)
            if c_id:
                self.id = c_id
            self.tags = list(set(self.tags + c_tags))
            self.paths = list(set(self.paths + c_paths))
            for k, v in c_params.items():
                self.parameters[k] = v

    def _apply_defaults(self):
        if not self.defaults:
            return  # No defaults section at all

        logger.debug("Applying bracket-based default metadata.")

        d_id, d_tags, d_paths, d_params = _parse_defaults_block(self.defaults)
        logger.debug(f"Default tags: {d_tags}")
        logger.debug(f"Default paths: {d_paths}")

        if not (d_id or d_tags or d_paths or d_params):
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

            # Add default paths to inherited_paths
            s.inherited_paths = list(s.inherited_paths)  # Make a copy
            s.inherited_paths.extend(d_paths)  # Add all default paths

            # Merge params: defaults first, then existing
            merged = dict(d_params)
            merged.update(s.inherited_params)
            s.inherited_params = merged

            logger.debug(
                f"Section after: id={s.id}, tags={s.tags}, inherited_tags={s.inherited_tags}, paths={s.paths}, inherited_paths={s.inherited_paths}"
            )

    def _parse_schema(self):
        """
        Parse the schema section for schema rules.

        This method supports two types of schema formats:
        1. Original bracket-based schema (for backward compatibility)
        2. FTML-based schema with improved validation capabilities
        """
        logger.debug("Parsing schema section.")

        if not self.schema:
            logger.debug("No schema section found.")
            return

        # First, check the content of the schema section for FTML schema
        content = self.schema.raw_content

        # Look for a line like [config]: ftml in the schema content
        ftml_schema_found = False
        rule_blocks = []
        current_block = []

        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue

            # Check if line defines a schema rule with FTML
            if line.startswith("[") and "]:" in line and "ftml" in line.lower():
                # If we had content in the current block, save it
                if current_block:
                    rule_blocks.append(current_block)
                    current_block = []

                # Start new block with this line
                current_block.append(line)
                ftml_schema_found = True
            elif current_block:
                # Continue existing block
                current_block.append(line)
            else:
                # Just add to current block
                current_block.append(line)

        # Don't forget the last block
        if current_block:
            rule_blocks.append(current_block)

        # Process the blocks
        if ftml_schema_found:
            for block in rule_blocks:
                if any("ftml" in line.lower() for line in block if "]:" in line):
                    # Process as FTML schema
                    self._parse_ftml_schema_block("\n".join(block))
                else:
                    # Process as traditional schema rule
                    self._parse_traditional_schema_block("\n".join(block))
        else:
            # No FTML schema found, use the original extended schema parser
            self._parse_extended_schema()

    def _parse_ftml_schema_block(self, block_content: str):
        """
        Parse an FTML schema block from the schema section.

        Args:
            block_content: Content of the FTML schema block
        """
        logger.debug("Parsing FTML schema block.")

        # Extract the section that contains FTML schema
        schema_section = None
        try:
            # Look for a line like: [config]: ftml
            match = re.search(r"\[(.*?)\]:\s*ftml", block_content)
            if match:
                section_id = match.group(1).strip()
                logger.debug(f"Found FTML schema section with ID: {section_id}")

                # Extract the FTML schema content
                content_lines = block_content.splitlines()
                for i, line in enumerate(content_lines):
                    if match.group(0) in line:
                        # Skip this line and extract the content until we find a [/
                        ftml_lines = []
                        j = i + 1
                        while j < len(content_lines) and not content_lines[
                            j
                        ].strip().startswith("[/"):
                            ftml_lines.append(content_lines[j])
                            j += 1
                        ftml_content = "\n".join(ftml_lines)

                        # Store the schema content
                        self.ftml_schema[section_id] = ftml_content

                        # Create a placeholder schema rule to track this section
                        rule = SchemaRule(
                            section_id=section_id,
                            tags=[],
                            paths=[],
                            parameters={},
                            type_name="ftml",  # Mark as FTML type
                            repetition_symbol=None,  # Required
                        )
                        self.schema_rules.append(rule)

                        break
        except Exception as e:
            logger.error(f"Error parsing FTML schema block: {str(e)}")
            # Continue with other schema processing

    def _parse_traditional_schema_block(self, block_content: str):
        """
        Parse a traditional schema rule block.

        Args:
            block_content: Content of the traditional schema block
        """
        logger.debug("Parsing traditional schema block.")
        try:
            lines = block_content.splitlines()
            parser = ExtendedSchemaParser(self.source_name)
            rules = parser.parse_schema_block(lines)
            self.schema_rules.extend(rules)
        except Exception as e:
            logger.error(f"Error parsing traditional schema block: {str(e)}")

    def _parse_extended_schema(self):
        """
        Original method to parse extended schema block.
        """
        logger.debug("Parsing extended schema block.")
        lines = self.schema.raw_content.splitlines()
        parser = ExtendedSchemaParser(self.source_name)
        self.schema_rules = parser.parse_schema_block(lines)

    def _parse_head_metadata_line(self, line: str):
        """
        Reuse from old logic: parse line into (id, tags, paths, params).
        Updated to handle @ prefix for paths.
        """
        tokens = shlex.split(line)
        if not tokens:
            return "", [], [], {}

        section_id = ""
        tags = []
        paths = []
        params = {}

        first = tokens[0]
        idx = 0
        if (
            not first.startswith("#")
            and not first.startswith("@")
            and not first.startswith(".")
            and "=" not in first
        ):
            section_id = first
            idx = 1

        while idx < len(tokens):
            t = tokens[idx]
            idx += 1
            if t.startswith("#"):
                tags.append(t)
            elif t.startswith("@"):
                paths.append(t)
            elif t.startswith("."):
                # Deprecated path syntax
                logger.warning(
                    f"Deprecated path syntax '.{t[1:]}' used in container metadata. "
                    f"Please use '@{t[1:]}' instead."
                )
                # Convert to new syntax internally
                paths.append("@" + t[1:])
            elif "=" in t:
                k, v = t.split("=", 1)
                k = k.strip()
                v = v.strip()
                val = parse_basic_value(v)
                params[k] = val
            else:
                params[t] = True

        return section_id, tags, paths, params

    def validate_schema(self):
        """
        Apply schema rules to self.sections.

        This method handles both traditional schema rules and FTML schema validation.
        """
        if not self.schema:
            logger.debug("No schema present. Skipping validation.")
            return

        # Process traditional schema rules first
        if self.schema_rules:
            logger.debug(
                f"Validating with {len(self.schema_rules)} traditional schema rules."
            )
            self._validate_traditional_schema()

        # Process FTML schema validation
        if self.ftml_schema:
            logger.debug(f"Validating with {len(self.ftml_schema)} FTML schemas.")
            self._validate_ftml_schema()

    def _validate_traditional_schema(self):
        """
        Apply traditional schema rules to self.sections in a strict order approach.
        """
        rule_queue = deque(self.schema_rules)
        sec_idx = 0
        n_secs = len(self.sections)

        while rule_queue:
            rule = rule_queue[0]
            needed = rule.repetition_symbol is None  # None => exactly one required
            optional = rule.repetition_symbol == "?"
            zero_plus = rule.repetition_symbol == "*"
            one_plus = rule.repetition_symbol == "+"

            if sec_idx >= n_secs:
                # no more actual sections
                if needed or one_plus:
                    raise SchemaSectionError(
                        f"Missing required section for schema rule '{rule.section_id}'."
                    )
                # else skip
                rule_queue.popleft()
                continue

            # Check if the next actual section matches
            current_sec = self.sections[sec_idx]
            if current_sec.id.lower() == rule.section_id.lower():
                # check tags, paths, params
                self._check_metadata_rule(rule, current_sec)
                # check content type
                if (
                    rule.type_name != current_sec.type_name.lower()
                    and rule.type_name not in ("*", "any")
                ):
                    raise SchemaTypeError(
                        f"Section '{current_sec.id}' has type '{current_sec.type_name}', "
                        f"but schema expects '{rule.type_name}'."
                    )

                # matched one occurrence
                sec_idx += 1
                if needed:
                    # exactly once => remove rule
                    rule_queue.popleft()
                elif optional:
                    # 0 or 1 => remove rule
                    rule_queue.popleft()
                elif one_plus:
                    # we matched one, so switch rule to '*'
                    # meaning any subsequent match is optional
                    rule_queue[0].repetition_symbol = "*"
                elif zero_plus:
                    # we can keep the same rule in queue if we want more
                    pass
            else:
                # next section doesn't match rule.section_id
                if optional or zero_plus:
                    # skip the rule
                    rule_queue.popleft()
                else:
                    # needed or one_plus => missing
                    raise SchemaSectionError(
                        f"Missing required section for schema rule '{rule.section_id}' "
                        f"but found '{current_sec.id}'."
                    )

        # if leftover actual sections appear => unexpected
        if sec_idx < n_secs:
            leftover_id = self.sections[sec_idx].id
            raise SchemaSectionError(
                f"Unexpected section '{leftover_id}' with no corresponding schema rule."
            )

    def _validate_ftml_schema(self):
        """
        Validate content of FTML sections against their respective schemas.
        """
        for schema_id, schema_content in self.ftml_schema.items():
            # Find matching sections
            matching_sections = [
                s for s in self.sections if s.id.lower() == schema_id.lower()
            ]

            if not matching_sections:
                logger.debug(f"No sections found matching schema ID: {schema_id}")
                continue

            # Validate each matching section
            for section in matching_sections:
                if section.type_name.lower() != "ftml":
                    logger.warning(
                        f"Section '{section.id}' has type '{section.type_name}' but schema expects 'ftml'. "
                        f"Skipping validation."
                    )
                    continue

                # Validate the raw content against the schema
                try:
                    # Pass the raw FTML content (not parsed data) to validation
                    errors = validate_ftml(section.raw_content, schema_content)

                    if errors:
                        error_msg = "\n".join(errors)
                        raise SchemaValidationError(
                            f"FTML validation errors for section '{section.id}':\n{error_msg}"
                        )

                    logger.debug(
                        f"FTML validation successful for section '{section.id}'"
                    )
                except Exception as e:
                    if isinstance(e, SchemaValidationError):
                        raise
                    raise SchemaValidationError(
                        f"FTML validation error for section '{section.id}': {str(e)}"
                    )

    def _check_metadata_rule(self, rule: SchemaRule, sec: Section):
        """
        Validate ID, tags, paths, parameters, etc. For example:
         - rule.tags must be present in sec.tags
         - rule.paths must be present in sec.paths
         - rule.parameters must match
        """
        # Check required tags
        for rt in rule.tags:
            base = rt.lstrip("#")
            if "#" + base not in sec.tags:
                raise SchemaSectionError(
                    f"Section '{sec.id}' missing required tag '{rt}'."
                )

        # Check required paths - handle both @ and . prefixes
        for rp in rule.paths:
            base = rp.lstrip("@").lstrip(".")
            path_found = False
            for sp in sec.paths:
                sp_base = sp.lstrip("@").lstrip(".")
                if sp_base == base:
                    path_found = True
                    break

            if not path_found:
                raise SchemaSectionError(
                    f"Section '{sec.id}' missing required path '{rp}'."
                )

        # Check required parameters
        for k, v in rule.parameters.items():
            if k not in sec.parameters:
                raise SchemaSectionError(
                    f"Section '{sec.id}' missing required param '{k}'."
                )
            if sec.parameters[k] != v:
                # or we can do type check
                raise SchemaSectionError(
                    f"Section '{sec.id}' param '{k}' != expected value '{v}'."
                )


##############################################################################
# COLLECTION CLASSES
##############################################################################


class SectionCollection:
    """
    Wraps a list of Section objects, giving them .help, etc.
    """

    def __init__(self, sections: List[Section]):
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

    def __init__(self, containers: List[Container]):
        self._containers = containers

    def __len__(self):
        return len(self._containers)

    def __getitem__(self, idx):
        return self._containers[idx]

    def __iter__(self):
        return iter(self._containers)


##############################################################################
# FLEX POINT AND FLEX MAP
##############################################################################


class FlexPoint:
    """
    A node with one or more sections plus child nodes keyed by string.
    """

    def __init__(self, parent_map=None, full_path=""):
        self.sections = []
        self.children = {}
        self._parent_map = parent_map
        self._full_path = full_path

    def add_section(self, sec: Section):
        self.sections.append(sec)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.sections[key]
        elif isinstance(key, str):
            return self.children[key]
        else:
            raise KeyError(key)


class FlexMap(dict):
    """
    A dictionary-like structure that organizes sections by ID or nested ID.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._all_rows = []

    def load_all_rows(self):
        """
        Rebuild the self._all_rows from the nested structure.
        """
        self._all_rows.clear()
        for k, v in self.items():
            self._collect_point_rows(f'["{k}"]', v)

    def _collect_point_rows(self, prefix: str, point: FlexPoint):
        n = len(point.sections)
        if n > 0:
            # If same type or mixed
            all_types = set(sec.type_name for sec in point.sections)
            if len(all_types) == 1:
                t = list(all_types)[0]
            else:
                t = "mixed"
            if n == 1:
                self._all_rows.append(
                    (prefix + "[0]", t, f"[[{point.sections[0].id}]]: {t}")
                )
            else:
                self._all_rows.append(
                    (prefix + f"[0..{n-1}]", t, f"[[{point.sections[0].id}]] x{n}")
                )
        for child_key, child_point in point.children.items():
            ch_prefix = prefix + f'["{child_key}"]'
            self._collect_point_rows(ch_prefix, child_point)


##############################################################################
# FLEX VIEW
##############################################################################


class FlexView:
    """
    Top-level container for multiple Container objects.
    You can filter or convert to a FlexMap, etc.
    """

    def __init__(self, containers: List[Container]):
        self._containers = containers
        self._raw_sections: List[Section] = []
        self._user_sections: List[Section] = []

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
                    # preserve container's special sections
                    new_c.container_metadata = c.container_metadata
                    new_c.defaults = c.defaults
                    new_c.schema = c.schema
                    new_c.id = c.id
                    new_c.tags = c.tags.copy()
                    new_c.paths = c.paths.copy()
                    new_c.parameters = c.parameters.copy()
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
        Handles tags (#tag), paths (@path), parameter expressions, and ID matching.
        """
        neg = False
        if token.startswith("!"):
            neg = True
            token = token[1:].strip()

        matched = False

        # Handle tag match (#tag)
        if token.startswith("#"):
            tag_pattern = token[1:]  # Remove '#'
            for tag in container.tags:
                tag_value = tag[1:] if tag.startswith("#") else tag
                if tag_value == tag_pattern:
                    matched = True
                    break

        # Handle path match (@path or .path)
        elif token.startswith("@") or token.startswith("."):
            path_pattern = token[1:]  # Remove @ or .
            for path in container.paths:
                path_value = (
                    path[1:] if path.startswith("@") or path.startswith(".") else path
                )
                if path_value == path_pattern:
                    matched = True
                    break

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
        # If token starts with '#', match tag
        if token.startswith("#"):
            pat = token[1:]
            return any((t[1:] if t.startswith("#") else t) == pat for t in sec.tags)

        # If token starts with '@', match path
        if token.startswith("@"):
            pat = token[1:]
            # Check for path matching (exact or hierarchical)
            for p in sec.paths:
                if p.startswith("@"):
                    p_val = p[1:]  # Remove @ prefix
                    # Match if path equals pattern or starts with pattern followed by .
                    if p_val == pat or p_val.startswith(pat + "."):
                        return True
            return False

        # If token starts with '.', match path (legacy)
        if token.startswith("."):
            pat = token[1:]
            # Check for path matching (exact or hierarchical)
            for p in sec.paths:
                if p.startswith("@") or p.startswith("."):
                    p_val = p[1:]  # Remove prefix
                    # Match if path equals pattern or starts with pattern followed by .
                    if p_val == pat or p_val.startswith(pat + "."):
                        return True
            return False

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

    def to_dict(self) -> dict:
        """
        Returns a Python dictionary representing this FlexView's sections
        in a simpler two-pass approach, ensuring repeated FTML lists
        remain separate in a list-of-lists.

        Rules:
          1. Sections with no ID => data[""] is the content directly if there's only one,
             or a list of contents if there are multiple.
             (raw => string, ftml => parsed object)
          2. Sections with an ID => data[id], or nested if using dot notation.
             If repeated, becomes a list of objects; if single occurrence, just that object.
             - raw => {"__raw": "..."}
             - ftml => the parsed FTML (list/dict/scalar)
        """

        # -----------------------------------------------------------------------
        # PASS 1: Collect all sections by ID in a dictionary of lists.
        #         This lets us see if an ID was repeated.
        # -----------------------------------------------------------------------
        collected = collections.defaultdict(list)

        for sec in self._raw_sections:
            stype = sec.type_name.lower()
            # Skip head sections
            if stype in ("container", "defaults", "schema"):
                continue

            # Build the object to store
            if stype == "raw":
                if sec.id == "":
                    # anonymous raw => raw string
                    item = sec.content
                else:
                    # raw with ID => {"__raw": "..."}
                    item = {"__raw": sec.content}
            elif stype in ("ftml", "yaml", "json", "toml"):
                # parsed result can be list/dict/scalar
                item = sec.content
            else:
                # fallback => raw content
                item = sec.raw_content

            # Append the item to the list for this ID
            collected[sec.id].append(item)

        # -----------------------------------------------------------------------
        # PASS 2: Build the final nested structure.
        #         - If an ID is repeated => store a list of items.
        #         - If single occurrence => store that single item.
        #         - Dot-splitting for nested IDs.
        #         - Anonymous ID => handle like other IDs (single -> direct, multiple -> list)
        # -----------------------------------------------------------------------
        def insert_nested(root: dict, segs: list, final_obj: Any):
            """Insert final_obj into root at segs. If segs is empty => root[""] list."""
            if not segs:
                # This would handle anonymous sections, but we bypass this for anonymous
                # by handling them directly outside of insert_nested
                return

            node = root
            for s in segs[:-1]:
                if s not in node or not isinstance(node[s], dict):
                    node[s] = {}
                node = node[s]
            last = segs[-1]
            if last not in node:
                node[last] = final_obj
            else:
                # If last is already used, convert to list or append
                existing = node[last]
                if isinstance(existing, list):
                    existing.append(final_obj)
                else:
                    node[last] = [existing, final_obj]

        result = {}

        for id_val, items in collected.items():
            if id_val == "":
                # Handle anonymous sections directly
                if len(items) == 1:
                    result[""] = items[0]  # Store single item directly
                else:
                    result[""] = items  # Store multiple items as a list
            else:
                # Handle sections with IDs with the original approach
                if len(items) == 1:
                    final_obj = items[0]  # single item
                else:
                    final_obj = items  # repeated => entire list
                segs = id_val.split(".")
                insert_nested(result, segs, final_obj)

        return result

    def to_flexmap(self) -> "FlexMap":
        """
        Convert all raw_sections into a nested FlexMap.
        If an ID is 'my_id' with no dots, we store the section
        directly in fm["my_id"]. If an ID is 'my.nested.id', we nest
        children accordingly.
        """
        logger.debug("Converting view to FlexMap.")
        fm = FlexMap()

        for sec in self._raw_sections:
            # Skip head sections
            s_type = sec.type_name.lower()
            if s_type in ("container", "defaults", "schema"):
                continue

            # If section has no ID, skip or store in anonymous
            if not sec.id:
                continue

            # Split on dot
            segs = sec.id.split(".")
            top_key = segs[0]

            # Ensure a top-level FlexPoint for that top_key
            if top_key not in fm:
                fm[top_key] = FlexPoint(parent_map=fm, full_path=f'["{top_key}"]')

            node = fm[top_key]
            prefix = f'["{top_key}"]'

            # If the ID has multiple segments (e.g. 'a.b.c'),
            # descend into node.children for segs[1:-1].
            for sub in segs[1:-1]:
                if sub not in node.children:
                    child_path = prefix + f'["{sub}"]'
                    node.children[sub] = FlexPoint(parent_map=fm, full_path=child_path)
                node = node.children[sub]
                prefix += f'["{sub}"]'

            # Now handle the last segment. If there's only 1 segment,
            # we add the Section directly to the top-level node.
            if len(segs) == 1:
                node.add_section(sec)
            else:
                last_seg = segs[-1]
                if last_seg not in node.children:
                    child_path = prefix + f'["{last_seg}"]'
                    node.children[last_seg] = FlexPoint(
                        parent_map=fm, full_path=child_path
                    )
                node.children[last_seg].add_section(sec)

        fm.load_all_rows()
        return fm


##############################################################################
# FLEXTAG
##############################################################################


class FlexTag:
    """
    Main entry point for loading .flextag or .ft files or raw strings.
    """

    def __init__(self, settings: Optional[FlexTagSettings] = None):
        self._parser = FlexParser()
        self.settings = settings if settings else FlexTagSettings()

    @classmethod
    def load(
        cls,
        path: Union[str, List[str], None] = None,
        string: Union[str, List[str], None] = None,
        dir: Union[str, List[str], None] = None,
        filter_query: Optional[str] = None,
        validate: bool = True,
        settings: Optional[FlexTagSettings] = None,
    ) -> FlexView:
        inst = cls(settings=settings)
        sources = inst._gather_sources(path, string, dir)
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
        path: Union[str, List[str], None],
        string: Union[str, List[str], None],
        dir: Union[str, List[str], None],
    ) -> List[str]:
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
                out.extend(self._dir_files(dir))
            else:
                for d in dir:
                    out.extend(self._dir_files(d))
        return out

    def _dir_files(self, directory: str) -> List[str]:
        res = []
        if not os.path.isdir(directory):
            return res
        for fn in os.listdir(directory):
            if fn.endswith(".flextag") or fn.endswith(".ft"):
                full_path = os.path.join(directory, fn)
                res.append(full_path)
        return res

    def _parse_source(self, src: str, source_name: str) -> Container:
        if os.path.exists(src) and os.path.isfile(src):
            logger.debug(f"Parsing file: {src}")
            with open(src, "r", encoding=self.settings.encoding) as f:
                lines = f.readlines()
        else:
            logger.debug("Parsing raw string input.")
            lines = src.splitlines(keepends=True)

        raw_secs = self._parser.parse_bracket_sections(lines, source_name)
        sections = []
        for rs in raw_secs:
            s_obj = Section(
                section_id=rs["section_id"],
                tags=rs["tags"],
                paths=rs["paths"],
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
    # Simple usage example
    example = r"""
[[]]: container
[my_file_id #file_tag @meta debug=true]
[[/]]

[[]]
text
[[/]]

[[items]]: ftml
[
  "apple",
  "banana",
  "orange"
]
[[/items]]

[[items]]: ftml
[
  "apple2",
  "banana2",
  "orange2"
]
[[/items]]

[[notes #draft @research]]
This is a text block by default
[[/notes]]

[[]]
text 2
[[/]]
"""
    view = FlexTag.load(string=example, validate=False)
    data = view.to_dict()
    print(data)
