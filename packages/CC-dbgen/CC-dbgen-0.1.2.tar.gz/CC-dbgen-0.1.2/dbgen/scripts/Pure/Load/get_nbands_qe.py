from typing import Tuple,Dict,Optional
import json
from dbgen.core.parsing import parse_line

def get_nbands_qe(files_params  : Tuple[str,str]) -> Optional[float]:
    """
    If we do have a params json, try to get nbands from it.
    """
    params_raw = files_params[1]
    if not params_raw:
        return None
    else:
        params = json.loads(params_raw)
        return params.get('nbands')     # no conceivable way of getting this from log
