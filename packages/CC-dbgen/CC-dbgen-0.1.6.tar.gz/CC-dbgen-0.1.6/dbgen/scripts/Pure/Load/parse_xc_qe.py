from typing import Dict

from dbgen.core.parsing import parse_line

def parse_xc_qe(log : str) -> str:
    """
    Finds the exchange correlation functional
    """
    parsed_line = parse_line(log,'Exchange-correlation',0)
    if parsed_line is None:
        raise ValueError
    else:
        raw_val       = parsed_line.split('=')[1].split()[0]
        processed_val = raw_val.replace(',','').replace("'",'')

        return  processed_val.strip()
