from typing import Tuple,Optional

def get_gamma_vasp(trip:Tuple[str,str,str]) -> Optional[int]:
    """
    Checks for gamma in KPOINTS
    """
    _,_,kptcar = trip
    return int('gamma' in kptcar)
