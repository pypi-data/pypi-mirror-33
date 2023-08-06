from typing import Dict,Tuple
import ast

from dbgen.core.parsing import parse_line

def get_kpts_vasp(trip:Tuple[str,str,str]) -> Tuple[int,int,int]:
    """
    Parse VASP kpt input from KPOINTS file
    """
    _,_,kptcar = trip
    line = kptcar.split('\n')[-2]
    raw  = [int(x) for x in line.split()]
    return tuple(raw) #type: ignore
