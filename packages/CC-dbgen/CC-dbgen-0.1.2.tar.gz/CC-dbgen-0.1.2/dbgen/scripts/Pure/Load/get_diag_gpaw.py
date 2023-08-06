from typing import Dict
from dbgen.core.parsing import parse_line

def get_diag_gpaw(log : str ) ->str:
    """
    Diagonalization algorithm.
    """
    parsed    = parse_line(log,'eigensolver',0)
    if parsed is None:
        raise ValueError('Malformed GPAW log file? can''t find "eigensolver"')
    else:
        eigenline = parsed.split(': ')[-1]
        if 'dav' in eigenline:
            return 'david'
        else:
            return eigenline
