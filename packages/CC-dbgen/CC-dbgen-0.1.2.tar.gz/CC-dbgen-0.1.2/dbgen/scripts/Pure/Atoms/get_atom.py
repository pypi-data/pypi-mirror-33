from typing import List,Tuple

import json
from ase import Atoms # type: ignore

def get_atom(atomsjson : str
            )->Tuple[List[str],List[int],List[int]
                        ,List[float],List[float],List[float]
                        ,List[int],List[float],List[int]]:
    """
    Helpful
    """
    atomdata = json.loads(atomsjson)['atomdata']
    output   = [(atomsjson
                ,a['index']
                ,a['number']
                ,a['x']
                ,a['y']
                ,a['z']
                ,a['constrained']
                ,a['magmom']
                ,a['tag']
                ) for a in atomdata]


    return tuple(map(list,zip(*output))) # type: ignore
