from typing import Tuple
from dbgen.core.parsing import parse_line
################################################################################
def get_maxstep_vasp(trip:Tuple[str,str,str]) -> int :
    """
    We need the dict instead of logfile because this info is only in pw.inp for QE
    """

    outcar,_,_ = trip
    parsed = parse_line(outcar,'NELM',0)
    if parsed is None:
        raise ValueError('malformed outcar?')
    else:
        raw = parsed.split('=')[1].strip().split()
        return int(raw[0].replace(';',''))
