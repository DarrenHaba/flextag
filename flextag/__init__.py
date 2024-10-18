"""
This is the __init__.py file for the flextag package.

It imports core functions for parsing and generating Flex Tag format.
"""

from .flextag import (  # noqa: F401
    flex_to_dict,
    dict_to_flex,
    flex_to_json,
    json_to_flex,
)
