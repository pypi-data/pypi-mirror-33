from typing import Dict,Optional
from dbgen.core.parsing import parse_line

def get_diag_vasp(log:str) -> Optional[str]:
    """
    Uh oh, guess we don't yet know how to extract which Diagonalization algo was used in VASP
    """
    return None
