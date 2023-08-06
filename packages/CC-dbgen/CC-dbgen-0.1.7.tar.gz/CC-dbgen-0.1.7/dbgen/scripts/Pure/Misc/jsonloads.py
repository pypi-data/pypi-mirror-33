from typing import Any
from json import loads

def jsonloads(x : str) -> Any:
    """
    Parses a JSON string
    """
    return loads(x)
