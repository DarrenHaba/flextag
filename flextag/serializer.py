from typing import Union, Dict, List


def dumps(data: Union[Dict, List]) -> str:
    """
    Serialize a Python data structure to a FlexTag string.

    Args:
        data (Union[Dict, List]): Data structure to serialize

    Returns:
        str: FlexTag formatted string

    Example:
        >>> import flextag
        >>> text = flextag.dumps({"test": "Hello World"})
        >>> print(text)
        ```flextag
        <<--[test]:
        Hello World
        ```
    """
    return Serializer().dumps(data)


class Serializer:
    """Internal serializer implementation"""

    def __init__(self):
        self.marker = "<<--"
        self.tag_terminator = ":"

    def dumps(self, data: Union[Dict, List]) -> str:
        """Internal dumps implementation"""
        # Basic implementation for now
        lines = ["```flextag"]

        if isinstance(data, dict):
            for key, value in data.items():
                lines.append(f"{self.marker}[{key}]{self.tag_terminator}")
                lines.append(str(value))

        lines.append("```")
        return "\n".join(lines)
