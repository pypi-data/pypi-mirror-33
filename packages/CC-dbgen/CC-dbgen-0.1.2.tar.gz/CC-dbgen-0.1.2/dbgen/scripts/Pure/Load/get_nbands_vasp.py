from typing import Dict,Optional,Tuple
import json
from dbgen.core.parsing import parse_line

def get_nbands_vasp(files_params : Tuple[str,str]) -> Optional[float]:
    """
    docstring
    """
    outcar = files_params[0]
    parsed = parse_line(outcar,'NBANDS',0)
    if parsed is None:
        raise ValueError('Malformed OUTCAR? No "NBANDS" found')
    else:
        nbands = parsed.split('=')[-1]
        return int(nbands)
