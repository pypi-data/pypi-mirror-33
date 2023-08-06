from typing import Dict,Optional
from dbgen.core.parsing import parse_line

def get_nmix_gpaw(log:str) -> Optional[float]:
    """
    Get the number of electronic steps mixed in for a new guess
    """
    parsed = parse_line(log,'nmaxold',0)
    if parsed is None:
        return 5 # default gpaw for systems with pbc
    else:
        raw    = parsed.split(':')[1].replace(',','')
        return float(raw)
