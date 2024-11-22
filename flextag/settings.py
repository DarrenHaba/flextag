class Const:
    """Constants for FlexTag syntax"""

    # Section markers
    PARAMS_START = "[[PARAMS"
    META_START = "[[META"
    SEC_START = "[[SEC"
    SEC_END = "[[/SEC]]"

    # Parameter prefixes
    TAG_PREFIX = "#"
    PATH_PREFIX = "."

    # Transport container markers
    TRANSPORT_START = "FLEXTAG__META_"
    TRANSPORT_META = "META_"
    TRANSPORT_DATA = "DATA_"
    TRANSPORT_END = "__FLEXTAG"

    # Default parameters
    DEFAULTS = {
        "fmt": "text",
        "enc": "utf-8",
        "crypt": "",
        "comp": "",
        "lang": "en"
    }

    # Parameter types
    PARAM_TYPES = {
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        "array": list
    }
