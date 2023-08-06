from typing import Dict
from dbgen.core.parsing import parse_line

def parse_pw_qe(log:str) -> int:
    """
    files   - a dictionary mapping file names to file content
    """
    # Constants
    #----------
    RYDBERG_TO_EV = 13.60569

    # Parsing
    #-------
    parsed      = parse_line(log,'kinetic-energy cutoff',0)
    if parsed is None:
        raise ValueError
    else:
        raw_rydberg = parsed.split()[-2]
        raw_num     = RYDBERG_TO_EV * float(raw_rydberg)
        return int(round(float(raw_num)))
