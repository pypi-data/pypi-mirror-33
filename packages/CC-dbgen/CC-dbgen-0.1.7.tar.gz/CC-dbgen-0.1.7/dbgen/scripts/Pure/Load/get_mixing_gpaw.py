from typing import Dict,Optional
from dbgen.core.parsing import parse_line

def get_mixing_gpaw(log:str) -> Optional[float]:
    """
    Helpful docstring
    """
    parsed = parse_line(log,'Linear mixing parameter',0)
    if parsed is None:
        raise ValueError
    else:
        raw    = parsed.split(':')[1]
        return round(float(raw),3)
