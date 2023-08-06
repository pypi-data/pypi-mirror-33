from typing import Dict

from dbgen.core.parsing import parse_line

def parse_xc_vasp(outcar:str) -> str:
    """
    Finds the exchange correlation functional
    """
    parsed = parse_line(outcar,'GGA  ',0)
    if parsed is None:
        raise ValueError('malformed OUTCAR? no "GGA  " string found')
    else:
        gga = parsed.split()[2] # <name> <equals sign> <GGA name>
        if gga == 'PE':
            return 'PBE' # need check for if BEEF?
        else:
            raise NotImplementedError('New functional in vasp? '+parsed)
