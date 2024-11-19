from typing import Optional


class FlexTagError(Exception):
    """Base exception for all FlexTag errors"""

    def __init__(self, message: str, example: Optional[str] = None):
        self.example = example
        if example:
            full_message = f"{message}\n\nExample of correct usage:\n{example}"
        else:
            full_message = message
        super().__init__(full_message)


class BlockError(FlexTagError):
    """Error in block syntax or structure"""

    def __init__(self, message: str):
        example = """<<--FT_BLOCK refs[config.dev]-->>
<<-- refs[database]:content-->>
<<--FT_BLOCK-->>"""
        super().__init__(f"Block Error: {message}", example)


class ItemError(FlexTagError):
    """Error in item syntax or structure"""

    def __init__(self, message: str):
        example = """<<-- refs[config.path, tag1]:
content here
-->>"""
        super().__init__(f"Item Error: {message}", example)


class ParameterError(FlexTagError):
    """Error in parameter syntax or values"""

    def __init__(self, message: str):
        example = """Parameter format should be: key[value]
Examples:
- refs[config.dev]
- fmt[json]
- ret[text]"""
        super().__init__(f"Parameter Error: {message}", example)


class TransportError(FlexTagError):
    """Error in transport container format"""

    def __init__(self, message: str):
        example = """----FT_CONTAINER--__enc.base64--content----FT_CONTAINER----"""
        super().__init__(f"Transport Error: {message}", example)
