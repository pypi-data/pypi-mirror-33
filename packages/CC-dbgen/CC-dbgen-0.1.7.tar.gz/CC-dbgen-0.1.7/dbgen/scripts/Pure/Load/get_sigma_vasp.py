from typing import Dict,Optional
from dbgen.core.parsing import parse_line

def get_sigma_vasp(outcar:str) -> Optional[float]:
    """
    Helpful docstring
    """

    parsed = parse_line(outcar,'SIGMA',0)
    if parsed is None:
        raise ValueError('malformed OUTCAR? no "SIGMA" found')
    else:
        raw    = parsed.split('=')[1].strip().split()[0]
        return float(raw)
