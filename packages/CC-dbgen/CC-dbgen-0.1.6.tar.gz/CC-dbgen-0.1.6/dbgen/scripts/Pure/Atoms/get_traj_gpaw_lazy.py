from typing import Dict,List,Tuple,Optional
# External modules
MbFloat = Optional[float]
ForceTuple = Tuple[int,int,MbFloat,MbFloat,MbFloat]
from ase        import Atoms # type: ignore
from string     import digits
from os.path    import join,exists
from os         import listdir
# Internal modules
from dbgen.core.numeric import roundfloat
################################################################################
def get_traj_gpaw_lazy(a_l_p : Tuple[str,str,str]) -> List[Tuple[Atoms,int,float,List[ForceTuple],int]]:
    """
    we don't do optimizations in gpaw???

    Returns list of triples to represent the trajectory of a structure during
    an optimization. The ASE structure, the step number along the trajectory,
    and the energy. These are parsed from a GPAW log file.
    """
    _,log,_ = a_l_p
    # Constants
    #---------
    output   = []
    forces   = [] # type: List[ForceTuple]
    stepnum  = 0
    FORCE = False
    CELL  = False
    POS   = False

    # Get log file
    #-------------
    lines = log.split('\n')
    for line in lines: # read NOT lazily
        # MAIN LOOP
        #----------
        if 'Positions:' in line:
            POS = True
            atomdata=[]
        elif 'Number of atoms' in line:
            num_atoms = int(line.split()[-1])
        elif POS:
            ind,sym,x,y,z = line.split()
            atomdata.append((sym,(roundfloat(x),roundfloat(y),roundfloat(z))))
            if int(ind)+1 == num_atoms:
                POS = False
        elif 'periodic' in line:
            CELL = True
            cellvecs =[]
        elif CELL:
            cellvecs.append([roundfloat(x) for x in line.split()[3:6]])
            if '3. axis' in line:
                CELL = False
                symbs = [a[0] for a in atomdata]
                pos   = [a[1] for a in atomdata]
                atoms = Atoms(symbols=symbs,positions=pos,cell=cellvecs)
                atoms.wrap()
        elif 'Forces in eV/Ang' in line:
            FORCE = True
            forces = []
        elif FORCE:
            if line.strip()=='':
                FORCE = False
            else:
                try:
                    i,_,fx,fy,fz = line.split()
                    forces.append((stepnum,int(i),roundfloat(fx),roundfloat(fy),roundfloat(fz)))
                except ValueError:
                    FORCE = False
                    forces =[]
        elif 'Extrapolated' in line:
            eng =float(line.split()[-1])

    if not forces:
        forces = [(0,i,None,None,None) for i in range(num_atoms)]

    output.append((atoms,stepnum,eng,forces,1))
    return output
