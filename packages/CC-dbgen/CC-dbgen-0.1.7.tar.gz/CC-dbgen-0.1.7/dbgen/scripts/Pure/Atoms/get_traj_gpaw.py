from typing import Dict,List,Tuple,Optional
MbFloat = Optional[float]
ForceTuple = Tuple[int,int,MbFloat,MbFloat,MbFloat]
from ase import Atoms,Atom # type: ignore
from string import digits
from os.path import join,exists

from dbgen.core.parsing import parse_line,btw
from dbgen.core.numeric import roundfloat
from dbgen.core.lists   import flatten
from dbgen.core.misc    import anytraj

def get_traj(stordir : str)->List[Tuple[Atoms,int,float,List[ForceTuple],int]]:
    """
    we don't do optimizations in gpaw???

    Returns list of triples to represent the trajectory of a structure during
    an optimization. The ASE structure, the step number along the trajectory,
    and the energy. These are parsed from a GPAW log file.
    """

    # Auxilliary Functions
    #---------------------
    def gpawl2cell(l:str)->list:
        return [roundfloat(x) for x in l.split()[-5:-2]]
    def parse_force(l:str)->ForceTuple:
        i,_,fx,fy,fz = l.split()
        return (0,int(i),float(fx),float(fy),float(fz))

    # Main Program
    #--------------

    with open(join(stordir,'log'),'r') as f: log = f.read()

    # Get atoms
    #-----------
    traj = anytraj(stordir)
    atom_text,atom_ind = btw(log,'Positions','Unit cell')

    a_lines = atom_text.split('\n')[1:-2]
    symbs,pos = [],[]
    for a in a_lines:
        items = a.split()
        symbs.append(items[1])
        pos.append(list(map(float,items[2:5])))


    # Get Cell
    #---------
    cell_text,cell_ind = btw(log,'periodic','Effective grid spacing',atom_ind)
    celllines = cell_text.split('\n')[1:-2]
    cell =[gpawl2cell(x) for x in celllines]

    # Get Energy
    #-----------
    eng =float(parse_line(log[cell_ind:],'Extrapolated:',-1).split()[-1])

    # Get Forces
    #----------
    force_text,_ = btw(log,'Forces in eV/Ang:','Timing',cell_ind)
    force_lines = force_text.strip().split('\n')[1:-1]
    # Put Atoms together
    #------------------
    atoms = Atoms(symbols=symbs,positions=pos,cell=cell
                ,constraint=traj.constraints,tags=traj.get_tags())

    atoms.wrap()
    # Handle case of not finding forces
    #---------------------------------
    if len(force_lines)==len(atoms):
        forces = [parse_force(x) for x in force_lines] # <- hack
    else:
        forces = [(0,i,None,None,None) for i in range(len(atoms))]


    return  [(atoms,0,eng,forces,1)]
