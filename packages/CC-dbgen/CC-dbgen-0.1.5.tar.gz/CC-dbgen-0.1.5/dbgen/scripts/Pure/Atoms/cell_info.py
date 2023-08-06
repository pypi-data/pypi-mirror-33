from typing import Tuple

def cell_info(ax:float
             ,ay:float
             ,az:float
             ,bx:float
             ,by:float
             ,bz:float
             ,cx:float
             ,cy:float
             ,cz:float
             ) -> Tuple[float,float,float,float,float]:
    """
    Details about a cell that we compute from its 3 defining vectors
    """
    surf_area = ((ax*bz-az*by) * (ay*bz - az*by)
                +(ax*bz-az*bx) * (ax*bz - az*bx)
                +(ax*by-ay*bx) * (ax*by - ay*bx)) ** 0.5

    vol = ( ax * (by * cz - bz * cy)
          - ay * (bx * cz - bz * cx)
          + az * (bx * cz - bz * cx))

    a   = (ax**2 + ay**2 + az**2)**0.5
    b   = (bx**2 + by**2 + bz**2)**0.5
    c   = (cx**2 + cy**2 + cz**2)**0.5

    return surf_area,vol,a,b,c
