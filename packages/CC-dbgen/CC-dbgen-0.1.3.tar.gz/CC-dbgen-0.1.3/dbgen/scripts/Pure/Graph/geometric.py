from typing import List
from ase import Atoms                      # type: ignore
from ase.data import covalent_radii,vdw_radii        # type: ignore
import numpy as np                         # type: ignore
from ase.neighborlist import NeighborList  # type: ignore
from json import dumps
from math import exp,isnan

def geometric(atoms:Atoms)->str:
    """
    If two atoms have a distance less than their covalent_radii sum, they're bonded
    (B.O. = e^(1-distance))
    """
    output     = [] # type: List


    pos        = atoms.get_positions()
    cell       = atoms.get_cell()
    cutoffs    = [covalent_radii[x]+0.25 for x in atoms.get_atomic_numbers()]
    nl = NeighborList(cutoffs           = cutoffs
                     ,skin              = 0
                     ,self_interaction  = False
                     ,bothways          = True)
    atoms.set_pbc([1,1,1])
    nl.update(atoms)
    for i in range(len(atoms)-1): # never need to check last one
        for j,(x,y,z) in zip(*nl.get_neighbors(i)):
            if i <= j:
                d = np.linalg.norm(pos[i]-pos[j]-np.dot([x,y,z],cell))
                pseudo_bo = round(3*exp(1-d),2)
                output.append([int(i),int(j),pseudo_bo,int(x),int(y),int(z)])

    return dumps(output)

if __name__=='__main__':
    import sys
    from ase.io import read # type: ignore
    print(geometric(read(sys.argv[1])))
