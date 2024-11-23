from typing import Optional


class FlexTagError(Exception):
    """Base exception for all FlexTag errors"""

    def __init__(self, message: str, example: Optional[str] = None):
        self.example = example
        super().__init__(
            f"{message}\n\nExample of correct usage:\n{example}" if example else message
        )


class ContainerError(FlexTagError):
    """Error in container format or structure"""

    def __init__(self, message: str):
        example = """[[PARAMS fmt="text" enc="utf-8"]]
[[META title="Example" #tag .path]]
[[SEC:config #system fmt="json"]]
content
[[/SEC]]"""
        super().__init__(f"Container Error: {message}", example)


class ParameterError(FlexTagError):
    """Error in parameter syntax or values"""

    def __init__(self, message: str):
        example = """Parameters should be space-separated with any quotes:
#tag1 #tag2 .path.to key=value key="value" key='value'
num=42 enabled=true items=[1,2,3] names=["a","b"]"""
        super().__init__(f"Parameter Error: {message}", example)


class FlexTagError(Exception):
    """Base exception for all FlexTag errors"""

    def __init__(self, message: str, example: Optional[str] = None):
        self.example = example
        super().__init__(
            f"{message}\n\nExample of correct usage:\n{example}" if example else message
        )


class SearchError(FlexTagError):
    """Error in search operations"""

    def __init__(self, message: str):
        example = """Valid searches:
- By ID: ":config"
- By tag: "#settings"
- By path: ".sys.config"
"""
        super().__init__(f"Search Error: {message}", example)


class EncodingError(FlexTagError):
    """Error in encoding/decoding operations"""

    def __init__(self, message: str):
        example = """Valid encodings:
- UTF-8 (default)
- ASCII
- ISO-8859-1"""
        super().__init__(f"Encoding Error: {message}", example)


class CompressionError(FlexTagError):
    """Error in compression/decompression operations"""

    def __init__(self, message: str):
        example = """Valid compression methods:
- gzip
- zip"""
        super().__init__(f"Compression Error: {message}", example)


class TransportError(FlexTagError):
    """Error in transport container format or processing"""

    def __init__(self, message: str):
        example = """FLEXTAG__META_<encoded_metadata>DATA_<encoded_data>__FLEXTAG"""
        super().__init__(f"Transport Error: {message}", example)
