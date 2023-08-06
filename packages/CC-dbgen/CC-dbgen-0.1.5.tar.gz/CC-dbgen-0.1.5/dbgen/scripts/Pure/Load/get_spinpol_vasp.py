from typing import Dict,Optional
from dbgen.core.parsing import parse_line

def get_spinpol_vasp(outcar:str) -> Optional[float]:
    """
    Docstring
    """

    parsed = parse_line(outcar,'ISPIN',0)
    if parsed is None:
        raise ValueError
    else:
        return int('1' in parsed)
