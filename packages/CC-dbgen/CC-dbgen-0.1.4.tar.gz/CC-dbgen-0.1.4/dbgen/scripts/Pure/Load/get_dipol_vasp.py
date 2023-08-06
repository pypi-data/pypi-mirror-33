from typing import Dict,Optional
import json
from dbgen.core.parsing import parse_line

def get_dipol_vasp(outcar : str) -> Optional[str]:
    """
    Docstring
    """
    line   = parse_line(outcar,' DIPOL')
    if line is None:
        return None
    else:
        print('parsing dipol line: '+line)
        raw    = line.split('=')[-1].split()
        output = [float(x) for x in raw]
        return json.dumps(output)
