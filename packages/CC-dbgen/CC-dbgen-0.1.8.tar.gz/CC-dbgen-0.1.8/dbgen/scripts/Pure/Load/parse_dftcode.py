from typing import Dict

from dbgen.core.parsing import parse_line

def parse_dftcode(logfile : str) -> str:
    """
    gets a dftcode, given the logfile identified in get_dft_logfiles
    """
    if 'POTCAR' in logfile[:2000]:
        return 'vasp'
    elif '___ ___ ___ _ _ _' in logfile[:500]:
            return 'gpaw'
    elif 'Quantum ESPRESSO' in logfile[:2000]:
        return 'quantumespresso'
    else:
        raise ValueError('could not determine DFT code ')
