from typing import Dict,Optional
from dbgen.core.parsing import parse_line

def get_sigma_qe(log:str
             ) -> Optional[float]:
    """
    Extract Fermi-Dirac smearing from QE log file
    """
    # constants
    #----------
    ryd_to_ev = 13.60569

    # main program
    #------------
    parsed = parse_line(log,'Fermi-Dirac smearing',0)
    if parsed is None:
        raise ValueError('malformed QE logfile?')
    else:
        raw = parsed.split()[-1]
        return round(ryd_to_ev * float(raw),3)
