from typing import Dict,Optional
from dbgen.core.parsing import parse_line

def get_spinpol_gpaw(log:str) -> Optional[int]:
    """
    Docstring
    """

    parsed = parse_line(log,'spinpol',0)
    if parsed is None:
        return 0
    else:
        return int('True' in parsed)
