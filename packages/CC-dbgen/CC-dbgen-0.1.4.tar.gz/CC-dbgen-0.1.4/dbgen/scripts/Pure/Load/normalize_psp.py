from typing import Dict
from dbgen.core.parsing import parse_line

def normalize_psp(pspth : str) -> str:
    """
    Normalizes pseudopotential name
    """

    if   'gbrv'   in pspth: return 'gbrv15pbe'
    elif 'sg15'   in pspth: return 'sg15'
    elif 'paw'    in pspth:  return 'paw'
    elif pspth[-6:] == 'LDA.gz':  return 'lda_paw'
    elif 'oldpaw'   == pspth:     return 'oldpaw'
    elif 'setups-0.8.7929' in pspth: return 'gpaw-setups-0.8.7929'
    elif '{}'       == pspth:     return '{}'
    elif 'dacapo' in pspth or 'esp-psp' in pspth or 'pslib' in pspth: return 'dacapo'
    else:
        raise NotImplementedError('New psp? path = ',pspth)
