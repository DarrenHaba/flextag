import re
from collections import OrderedDict


def flex_to_dict(flex_tag_string):
    """
    Parse a Flex Tag formatted string into an OrderedDict to maintain tag order.
    """
    tag_dict = OrderedDict()
    current_tag = None
    tag_stack = []

    lines = flex_tag_string.splitlines()

    for line in lines:
        line = line.strip()  # Remove any indentation

        # Check for opening tag
        opening_tag_match = re.match(r"\[\[---- (.+) --", line)
        if opening_tag_match:
            tag_name = opening_tag_match.group(1).strip()
            if current_tag:
                # Push current tag to stack to handle nested tags
                tag_stack.append((current_tag, tag_dict))
                tag_dict = OrderedDict()
            current_tag = tag_name
            continue

        # Check for closing tag
        if line == "--]]":
            if tag_stack:
                # If there is a nested tag, pop the parent tag from stack
                parent_tag, parent_dict = tag_stack.pop()
                parent_dict[current_tag] = tag_dict
                tag_dict = parent_dict
                current_tag = parent_tag
            else:
                current_tag = None
            continue

        # Add content to current tag
        if current_tag:
            if current_tag not in tag_dict:
                tag_dict[current_tag] = ""
            tag_dict[current_tag] += line + "\n"

    # Clean up any trailing newline characters in strings
    for key in tag_dict:
        if isinstance(tag_dict[key], str):
            tag_dict[key] = tag_dict[key].strip()

    return tag_dict


def dict_to_flex(tag_dict):
    """
    Convert a nested OrderedDict back into a Flex Tag formatted string.
    """
    flex_tag_string = ""

    def recursive_build_flex_tag(d, depth=0):
        nonlocal flex_tag_string
        for key, value in d.items():
            indent = " " * (depth * 2)  # optional indentation based on depth
            flex_tag_string += f"{indent}[[---- {key} --\n"
            if isinstance(value, dict):
                recursive_build_flex_tag(value, depth + 1)  # Recurse into nested dict
            else:
                flex_tag_string += f"{indent}{value}\n"
            flex_tag_string += f"{indent}--]]\n"

    recursive_build_flex_tag(tag_dict)
    return flex_tag_string.strip()
