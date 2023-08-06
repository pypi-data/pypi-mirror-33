# External Modules
from typing  import Dict,List,Tuple,Optional
from ase     import Atoms # type: ignore
from os.path import join,exists
# Internal Modules
from dbgen.core.numeric import roundfloat
from dbgen.core.lists   import flatten
from dbgen.core.misc    import wrap
from dbgen.scripts.Pure.Atoms.json_to_traj   import json_to_traj

ForceTuple = Tuple[int,int,Optional[float],Optional[float],Optional[float]]
################################################################################
def get_traj_vasp_lazy(a_l_p : Tuple[str,str,str])->List[Tuple[Atoms,int,float,List[ForceTuple],int]]:
    """
    Returns list of quadruples to represent the trajectory of a structure during
    an optimization.
        - ASE structure,
        - the step number along the trajectory,
        - the energy
        - the forces.

    These are parsed from VASP's OUTCAR and POSCAR.
    """
    # Initialize
    #-----------
    anytraj,outcar,poscar = a_l_p
    output   = []
    CELL     = False
    POSFORCE = False
    cellvecs = [] # contains up to three entries like [0.000,1.15,16.324]
    pos = [] # contains many (X,Y,Z) tuples
    forces   = []
    stepnum  = 0  # step in the trajectory
    atomcounter = 0
    traj  = json_to_traj(anytraj)

    # Prequel: extract the list of chemical symbols from POSCAR in a convoluted way
    #-----------------------------------------------------------------------------
    plines = poscar.split('\n')
    uniqsymbs = plines[0].split() # ['H','O','Na']
    quantities = plines[5].split() # ['2','1','5']
    symbs = flatten([[a]*int(b) for a,b in zip(uniqsymbs,quantities)]) # ['H','H','O','Na','Na','Na','Na','Na']

    # Get log file
    #-------------
    with open(outcar,'r') as f:
        for line in f: # read lazily

            # MAIN LOOP
            #----------
            if 'reciprocal lattice vectors' in line:
                CELL = True
                cellvecs = []
            elif CELL and len(cellvecs)<3:
                cellvecs.append([roundfloat(x) for x in line.split()[:3]])
            elif CELL and 'length of vectors' in line:
                CELL = False

            elif 'POSITION' in line:
                POSFORCE = True
            elif POSFORCE and '---' not in line:
                if 'total drift' in line:
                    POSFORCE = False
                else:
                    x,y,z,fx,fy,fz = line.split()
                    pos.append([roundfloat(x),roundfloat(y),roundfloat(z)])
                    forces.append((stepnum,atomcounter,fx,fy,fz))
                    atomcounter +=1
            elif "free  energy   TOTEN" in line:
                e = float(line.split()[-2])
                atoms = Atoms(symbols=symbs,positions=pos,cell=cellvecs
                             ,constraint=traj.constraints,tags=traj.get_tags())
                wrap(atoms)
                for a in atoms:
                    assert a.z >= 0
                output.append((atoms,stepnum,e,forces,0))
                atomcounter = 0
                cellvecs,pos,forces = [],[],[]
                stepnum  += 1   # step in the trajectory


    output[-1] = tuple([*output[-1][:-1],1]) # set final for finaltraj
    return output
