from typing import Dict,Optional
from dbgen.core.parsing import parse_line

def get_diag_qe(log : str) -> Optional[str]:
    """
    Diagonalization algorithm
    """
    if 'Davidson diagonalization' in log:
        return 'david'
    else:
        parsed = parse_line(log,'diagonalization',0)
        if parsed is None:
            return None
        else:
            if 'Davidson' in parsed:
                return 'david'
            else:
                raise NotImplementedError('new diag routine in QE? '+parsed)
