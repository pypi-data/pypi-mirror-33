from typing import Dict
from dbgen.core.parsing import parse_line

def get_dipole_qe(log:str) -> int:
    """
    Parse pw.inp file to see if dipole correction was applied
    """
    return int('Computed dipole' in log)
