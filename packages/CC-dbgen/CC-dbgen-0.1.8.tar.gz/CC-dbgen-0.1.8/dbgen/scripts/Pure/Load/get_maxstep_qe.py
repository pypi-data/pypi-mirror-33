from typing import Tuple
from dbgen.core.parsing import parse_line

def get_maxstep_qe(trip:Tuple[str,str,str]) -> int :
    """
    We need the dict instead of logfile because this info is only in pw.inp?
    """
    _,pwinp,_  = trip
    parsed = parse_line(pwinp,'electron_maxstep',0)
    if parsed is None:
        raise ValueError('malformed pw.inp?')
    else:
        return int(parsed.split('=')[1][:-1])
