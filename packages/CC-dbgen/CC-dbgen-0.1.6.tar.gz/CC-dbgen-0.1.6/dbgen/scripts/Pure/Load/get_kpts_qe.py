from typing import Dict,Tuple

def get_kpts_qe(trip:Tuple[str,str,str]) -> Tuple[int,int,int]:
    """
    K point info (? ? ? kx ky kz) assumed to be in penultimate line of pw.inp
    """

    _,pwinp,_ = trip
    line  = pwinp.split('\n')[-1]
    raw   = line.split()[:3]
    return tuple([int(x) for x in raw])    #type: ignore
