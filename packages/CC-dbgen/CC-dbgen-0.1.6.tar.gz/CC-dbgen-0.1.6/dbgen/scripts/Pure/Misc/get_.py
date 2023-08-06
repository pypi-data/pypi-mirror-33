from typing import Any,Dict

def get_(d       : Dict[Any,Any]
        ,key     : str
        ,default : Any              = None
        ) -> Any:
    """
    Gets a key from a dictionary
    """
    return d.get(key,default)
