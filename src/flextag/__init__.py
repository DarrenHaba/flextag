"""
FlexTag - Public API

This module provides the main entry points for the FlexTag library:
- load(...) -> parse FlexTag data into a FlexView with rich querying abilities
- validate(...) -> validate FlexTag content against schema rules
- filter(...) -> filter sections or containers using query language
"""

from typing import List, Optional, Union

from .flextag import (
    FlexTag,
    FlexTagError,
    FlexTagSettings,
    FlexTagSyntaxError,
    FlexView,
    SchemaSectionError,
    SchemaTypeError,
    SchemaValidationError,
    logger,
)

# Version constants
FLEXTAG_VERSION = "0.4.0a1"  # The FlexTag specification version
PACKAGE_VERSION = "0.4.0a1"  # The package version - update with each release


def get_flextag_version():
    """Return the FlexTag specification version this parser implements."""
    return FLEXTAG_VERSION


def get_package_version():
    """Return the package version."""
    return PACKAGE_VERSION


def load(
    path: str | list[str] | None = None,
    string: str | list[str] | None = None,
    dir: str | list[str] | None = None,
    filter_query: str | None = None,
    validate: bool = True,
    settings: FlexTagSettings | None = None,
    recursive: bool = True,
) -> FlexView:
    """
    Parse FlexTag data from files, strings, or directories.

    Args:
        path: File path(s) to FlexTag content
        string: Raw FlexTag string content
        dir: Directory path(s) containing FlexTag files (.flextag or .ft)
        filter_query: Optional query to filter containers after loading
        validate: Whether to validate against any embedded schema
        settings: Optional settings to control parsing behavior
        recursive: Whether to recursively search subdirectories when using dir=
                   (default: True)

    Returns:
        A FlexView object containing the parsed sections and containers

    Raises:
        FlexTagError: Base class for all FlexTag-related errors
        FlexTagSyntaxError: If there is a syntax error in the FlexTag content
        SchemaValidationError: If validation fails against the schema
    """
    return FlexTag.load(
        path=path,
        string=string,
        dir=dir,
        filter_query=filter_query,
        validate=validate,
        settings=settings,
        recursive=recursive,
    )


def filter(view: FlexView, query: str, target: str = "sections") -> FlexView:
    """
    Filter a FlexView by sections or containers using query syntax.

    Args:
        view: The FlexView to filter
        query: Query string using FlexTag's filter syntax
        target: Whether to filter "sections" or "containers"

    Returns:
        A new filtered FlexView containing only the matched elements
    """
    return view.filter(query, target)


def configure_settings(**kwargs) -> FlexTagSettings:
    """
    Create a FlexTagSettings object with custom settings.

    Args:
        **kwargs: Settings to override (allow_directory_traversal,
                 allow_remote_loading, max_section_size, etc.)

    Returns:
        A configured FlexTagSettings object for use with load()
    """
    settings = FlexTagSettings()
    for key, value in kwargs.items():
        if hasattr(settings, key):
            setattr(settings, key, value)
    return settings


# Make these available in the public API
__all__ = [
    "load",
    "filter",
    "configure_settings",
    "FlexView",
    "FlexTagSettings",
    "FlexTagError",
    "FlexTagSyntaxError",
    "SchemaValidationError",
    "SchemaTypeError",
    "SchemaSectionError",
    "logger",
    "get_flextag_version",
    "get_package_version",
]
