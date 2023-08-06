from typing import Tuple
from dbgen.core.parsing import parse_line

def get_maxstep_gpaw(trip:Tuple[str,str,str]) -> int :
    """
    We need the dict instead of logfile because this info is only in pw.inp for QE
    """

    log,_,_ = trip
    parsed  = parse_line(log,'maxiter',0)
    if parsed is None:
        return 333 # default GPAW value
    else:
        return int(parsed.split(':')[-1])
