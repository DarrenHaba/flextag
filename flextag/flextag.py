"""
Utilities for converting between Flex Tag, Python dictionaries, and JSON.

This module contains four primary functions:
- `flex_to_dict`: Parses a Flex Tag formatted string into an OrderedDict.
- `dict_to_flex`: Converts a nested OrderedDict or dict back into a Flex Tag
  formatted string.
- `flex_to_json`: Converts a Flex Tag formatted string to a JSON string.
- `json_to_flex`: Converts a JSON string to a Flex Tag formatted string.
"""

import re
import json
from collections import OrderedDict
from typing import Union, Any, List, Tuple


def flex_to_dict(flex_tag_string: str) -> OrderedDict:
    """
    Parse a Flex Tag formatted string into an OrderedDict to maintain tag order.

    This function takes a string formatted with Flex Tags and converts it into a nested
    OrderedDict structure. It supports nested tags and preserves the order of tags.

    Args:
        flex_tag_string: A string containing content formatted with Flex Tags.

    Returns:
        A nested OrderedDict where keys are tag names and values are either
        strings (for content) or nested OrderedDicts (for nested tags).

    Examples:
        >>> flex_string = '''
        ... [[-- text
        ... Hello, World!
        ... --]]
        ... [[-- python code
        ... print("Hello, World!")
        ... --]]
        ... '''
        >>> result = flex_to_dict(flex_string)
        >>> print(result)
        OrderedDict([
            ('text', 'Hello, World!'),
            ('python code', 'print("Hello, World!")')
        ])
    """
    tag_dict = OrderedDict()
    current_tag = None
    tag_stack = []
    content_lines = []

    lines = flex_tag_string.splitlines()

    for line in lines:
        # Check for opening tag
        opening_tag_match = re.match(r"\s*\[\[-- (.+)", line)
        if opening_tag_match:
            if current_tag:
                tag_dict[current_tag] = "\n".join(content_lines).rstrip()
                content_lines = []
            tag_name = opening_tag_match.group(1).strip()
            if current_tag:
                tag_stack.append((current_tag, tag_dict))
                tag_dict = OrderedDict()
            current_tag = tag_name
            continue

        # Check for closing tag
        if line.strip() == "--]]":
            if content_lines:
                tag_dict[current_tag] = "\n".join(content_lines).rstrip()
                content_lines = []
            if tag_stack:
                parent_tag, parent_dict = tag_stack.pop()
                parent_dict[current_tag] = tag_dict
                tag_dict = parent_dict
                current_tag = parent_tag
            else:
                current_tag = None
            continue

        # Add content to current tag
        if current_tag:
            content_lines.append(line)

    # Handle any remaining content
    if current_tag and content_lines:
        tag_dict[current_tag] = "\n".join(content_lines).rstrip()

    return tag_dict


def dict_to_flex(tag_dict: Union[OrderedDict, dict]) -> str:
    """
    Convert a nested OrderedDict or dict back into a Flex Tag formatted string.

    This function takes a nested dictionary structure (either OrderedDict or regular
    dict) and converts it into a Flex Tag formatted string. It supports nested
    structures and preserves the order of keys if an OrderedDict is used.

    Args:
        tag_dict: A nested dictionary structure where keys are tag names and values are
                  either strings (for content) or nested dictionaries (for nested tags).

    Returns:
        A Flex Tag formatted string representing the input dictionary structure.

    Examples:
        >>> tag_dict = OrderedDict([
        ...     ('text', 'Hello, World!'),
        ...     ('python code', 'print("Hello, World!")')
        ... ])
        >>> result = dict_to_flex(tag_dict)
        >>> print(result)
        [[-- text
        Hello, World!
        --]]

        [[-- python code
        print("Hello, World!")
        --]]
    """
    flex_tag_string = ""

    def recursive_build_flex_tag(d: Union[OrderedDict, dict], depth: int = 0) -> None:
        nonlocal flex_tag_string
        for key, value in d.items():
            indent = " " * (depth * 2)  # optional indentation based on depth
            flex_tag_string += f"{indent}[[-- {key}\n"
            if isinstance(value, dict):
                recursive_build_flex_tag(value, depth + 1)  # Recurse into nested dict
            else:
                flex_tag_string += f"{indent}{value}\n"
            flex_tag_string += f"{indent}--]]\n\n"

    recursive_build_flex_tag(tag_dict)
    return flex_tag_string.strip()


def flex_to_json(flex_tag_string: str, indent: int = None) -> str:
    r"""
    Convert a Flex Tag formatted string to a JSON string.

    Args:
        flex_tag_string: A string containing content formatted with Flex Tags.
        indent: Number of spaces for indentation in the resulting JSON string.
                If None, the JSON will be compact. Defaults to None.

    Returns:
        A JSON formatted string representing the input Flex Tag structure.

    Example:
        >>> flex_string = '''
        ... [[-- text
        ... Hello, World!
        ... --]]
        ... [[-- python code
        ... print("Hello, World!")
        ... --]]
        ... '''
        >>> json_string = flex_to_json(flex_string, indent=2)
        >>> print(json_string)
        {
          "text": "Hello, World!",
          "python code": "print(\"Hello, World!\")"
        }
        >>> compact_json = flex_to_json(flex_string)
        >>> print(compact_json)
        {"text": "Hello, World!", "python code": "print(\"Hello, World!\")"}
    """
    tag_dict = flex_to_dict(flex_tag_string)
    return json.dumps(tag_dict, indent=indent)


def json_to_flex(json_string: str) -> str:
    r"""
    Convert a JSON string to a Flex Tag formatted string.

    This function takes a JSON formatted string, converts it to an OrderedDict,
    and then converts that OrderedDict to a Flex Tag formatted string using the
    dict_to_flex function.

    Args:
        json_string: A JSON formatted string.

    Returns:
        A Flex Tag formatted string representing the input JSON structure.

    Examples:
        >>> json_string = ('{"text": "Hello, World!", '
        ...                '"python code": "print(\\"Hello, World!\\")"}')
        >>> result = json_to_flex(json_string)
        >>> print(result)
        [[-- text
        Hello, World!
        --]]

        [[-- python code
        print("Hello, World!")
        --]]
    """

    def ordered_dict_hook(pairs: List[Tuple[Any, Any]]) -> OrderedDict:
        return OrderedDict(pairs)

    tag_dict = json.loads(json_string, object_pairs_hook=ordered_dict_hook)
    return dict_to_flex(tag_dict)
