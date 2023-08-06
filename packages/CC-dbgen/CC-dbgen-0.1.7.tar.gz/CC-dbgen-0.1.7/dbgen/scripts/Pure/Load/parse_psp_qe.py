from typing import Dict
from dbgen.core.parsing import parse_line

def parse_psp_qe(log :str) -> str:
    """
    Returns simplified string representation of the pseudopotnetial used in a
    DFT calculation
    """
    pseudoline = parse_line(log,'pseudo dir',0)
    if pseudoline is None:
        raise ValueError('malformed QE log file? can''t find "pseudo dir"')
    else:
        return pseudoline.split(":")[1].strip()
