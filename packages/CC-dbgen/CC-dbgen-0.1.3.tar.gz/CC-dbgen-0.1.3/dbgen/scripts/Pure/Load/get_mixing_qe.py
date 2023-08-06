from typing import Dict,Optional
from dbgen.core.parsing import parse_line

def get_mixing_qe(log:str) -> Optional[float]:
    """
    Get mixing beta from QE log file
    """

    parsed = parse_line(log,'mixing_beta',0) or parse_line(log,'mixing beta',0)  # different QE versions?
    if parsed is None:
        raise ValueError
    else:
        raw    = parsed.split("=")[1]
        return round(float(raw),3)
