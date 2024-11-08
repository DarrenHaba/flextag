import json
from typing import Union, Dict, List


def to_json(data: Union[Dict, List]) -> str:
    """
    Convert FlexTag data structure to JSON string.

    Args:
        data (Union[Dict, List]): FlexTag data structure

    Returns:
        str: JSON string
    """
    return json.dumps(data)


def from_json(json_str: str) -> Union[Dict, List]:
    """
    Convert JSON string to FlexTag data structure.

    Args:
        json_str (str): JSON string

    Returns:
        Union[Dict, List]: FlexTag data structure
    """
    return json.loads(json_str)
