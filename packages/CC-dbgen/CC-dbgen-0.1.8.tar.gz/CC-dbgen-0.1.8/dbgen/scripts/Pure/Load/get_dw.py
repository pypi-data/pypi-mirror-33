from typing import Dict,Optional

from dbgen.core.parsing import parse_line

def get_dw(dftcode : str
          ,log : str
          ) -> Optional[int]:
    """
    Density wave cutoff, only meaningful for quantumespresso
    """
    # Constants
    #-----------
    ryd_to_ev =  13.60569

    # Main Program
    #-------------

    if  dftcode == 'quantumespresso':
        parsed = parse_line(log,'charge density cutoff',0)
        if parsed is None:
            raise ValueError
        else:
            raw    = parsed.split('=')[1][:7]
            return round(ryd_to_ev * float(raw))
    else:
        return None
