class Const:
    """Constants for FlexTag syntax"""

    # Settings tag - no end tag required
    SETTINGS = "[[SETTINGS"

    # Info tags with full syntax
    INFO_START = "[[INFO"
    INFO_END = "[[/INFO]]"

    # Section tags with full syntax
    SEC_START = "[[SEC"
    SEC_END = "[[/SEC]]"

    # Marker prefixes
    TAG_PREFIX = "#"
    PATH_PREFIX = "."

    # Parameter syntax
    PARAM_START = "{"
    PARAM_END = "}"
    PARAM_SEP = ","
    PARAM_ASSIGN = "="
    PARAM_QUOTE = '"'

    # Color scheme for syntax highlighting
    COLORS = {
        "settings": "#8B0000",  # Dark Red
        "info": "#006400",  # Dark Green
        "section": "#4B0082",  # Indigo
        "tag": "#8B4513",  # Saddle Brown
        "path": "#2F4F4F",  # Dark Slate Gray
        "param": "#696969",  # Dim Gray
        "content": "#000000",  # Black
        "error": "#FF0000",  # Red
    }
