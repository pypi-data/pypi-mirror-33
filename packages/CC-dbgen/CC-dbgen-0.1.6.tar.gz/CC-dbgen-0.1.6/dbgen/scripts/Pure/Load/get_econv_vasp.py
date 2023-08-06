from typing import Dict,Optional
from dbgen.core.parsing import parse_line

def get_econv_vasp(outcar : str) -> Optional[float]:
    """
    Electronic energy convergence from INCAR
    """


    parsed = parse_line(outcar,'EDIFF',0)
    if parsed is None:
        raise ValueError('malformed OUTCAR? no "EDIFF" found')
    else:
        raw    = parsed.split('=')[1].strip().split()[0]
        return float(raw)
