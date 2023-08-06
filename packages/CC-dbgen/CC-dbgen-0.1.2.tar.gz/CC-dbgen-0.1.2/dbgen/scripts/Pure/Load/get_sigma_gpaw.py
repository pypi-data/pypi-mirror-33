from typing import Dict,Optional
from dbgen.core.parsing import parse_line

def get_sigma_gpaw(log:str) -> Optional[float]:
    """
    Helpful docstring
    """
    parsed = parse_line(log,'Fermi-Dirac',0)
    if parsed is None:
        raise ValueError
    else:
        raw = parsed.split('=')[1].split()[0]
        return float(raw)
