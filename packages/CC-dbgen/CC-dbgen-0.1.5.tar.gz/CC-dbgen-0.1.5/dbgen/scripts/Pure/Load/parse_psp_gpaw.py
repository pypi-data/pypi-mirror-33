from typing import Dict
from dbgen.core.parsing import parse_line

def parse_psp_gpaw(log:str) -> str:
    """
    Returns simplified string representation of the pseudopotnetial used in a
    DFT calculation
    """
    rawpspth = parse_line(log,'setups',0)

    if rawpspth is None:
        return 'paw' # default
    else:
        pspth = rawpspth.split(': ')[-1].strip()
        if 'gpaw-setups-0.6.6300' in pspth:
            return 'oldpaw'
        elif 'setups/' == pspth[:7]:
            return 'paw'
        else:
            return pspth
