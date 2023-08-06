from typing import Dict,Optional
from dbgen.core.parsing import parse_line

def get_mixtype(dftcode : str
               ,log     : str
               ) -> Optional[str]:
    """
    Helpful docstring
    """

    if dftcode == 'quantumespresso':
        parsed = parse_line(log,'number of iterations used',0)
        if parsed is None:
            return None
        else:
            return parsed.split()[6]

    else:
        return None
