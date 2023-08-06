from typing import Dict
from dbgen.core.parsing import parse_line

def get_dipole_vasp(outcar:str) -> int:
    """
    Parse INCAR to detect if dipole correction was applied
    """
    parsed = parse_line(outcar,'LDIPOL',0)
    if parsed is None:
        raise ValueError('malformed OUTCAR? no "LDIPOL" found')
    else:
        return int(' T ' in parsed)
