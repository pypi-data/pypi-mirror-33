from typing import Dict
from dbgen.core.parsing import parse_line

def get_dipole_gpaw(log:str) -> int:
    """
    Until we figure out how to actually get dipole correction to work,
    assume that it's always turned off
    """

    return 0
