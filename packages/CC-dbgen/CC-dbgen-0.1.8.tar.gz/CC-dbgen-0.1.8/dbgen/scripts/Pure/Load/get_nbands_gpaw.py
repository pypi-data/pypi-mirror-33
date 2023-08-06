from typing import Dict,Optional,Tuple
import json
from dbgen.core.parsing import parse_line

def get_nbands_gpaw(files_params  : Tuple[str,str]
              ) -> Optional[int]:
    """
    If we do have a params json, try to get nbands from it.
    """
    params_raw = files_params[1]
    if not params_raw:
        return None
    else:
        params = json.loads(params_raw)
        return int(params.get('nbands'))     # no conceivable way of getting this from log
