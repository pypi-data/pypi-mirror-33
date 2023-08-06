from typing import Dict,Tuple
import ast

from dbgen.core.parsing import parse_line

def get_kpts_gpaw(trip:Tuple[str,str,str]) -> Tuple[int,int,int]:
    """
    docstring
    """
    log,_,_    = trip
    parsed = parse_line(log,'k-points: ')
    if parsed is None:
        return (1,1,1) # default
    else:
        raw    = parsed.split(': ')[1].split()
        return (int(raw[0]),int(raw[2]),int(raw[4]))
