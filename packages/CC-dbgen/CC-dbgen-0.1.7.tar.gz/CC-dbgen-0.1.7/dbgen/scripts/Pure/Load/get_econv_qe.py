from typing import Dict,Optional
from dbgen.core.parsing import parse_line

def get_econv_qe(log : str
             ) -> Optional[float]:
    """
    Electronic energy convergence from pw.inp file
    """

    # Constants
    #----------
    ryd_to_ev = 13.60569

    # main program
    #------------
    line = parse_line(log,'convergence threshold',0)
    if line is None:
        raise ValueError('malformed QE logfile ? no "convergence threshold" found')
    else:
        raw = line.split('=')[-1]
        return round(ryd_to_ev * float(raw),6)
