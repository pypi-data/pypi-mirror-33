from typing import Dict,Optional
from dbgen.core.parsing import parse_line

def get_spinpol_qe(log : str) -> Optional[float]:
    """
    Docstring
    """

    return int('magnetization' in log)
