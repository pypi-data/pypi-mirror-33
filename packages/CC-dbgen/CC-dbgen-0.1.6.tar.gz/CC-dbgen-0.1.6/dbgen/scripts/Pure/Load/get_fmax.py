from typing import Dict,Optional
import json
from dbgen.core.parsing import parse_line

def get_fmax(dftcode     : str
            ,paramsdict  : str
            ,outcar      : str
            ) -> Optional[float]:
    """
    docstring
    """
    if dftcode == 'vasp':
        return -float(parse_line(outcar,'EDIFFG').split('=')[-1])
    else:
        params = json.loads(paramsdict)
        return params.get('fmax')     # no conceivable way of getting this from log
