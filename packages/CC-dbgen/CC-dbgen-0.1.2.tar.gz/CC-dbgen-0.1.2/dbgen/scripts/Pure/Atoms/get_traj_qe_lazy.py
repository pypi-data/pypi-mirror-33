# External Modules
from typing     import List,Tuple,Optional
from ase        import Atoms # type: ignore
from string     import digits
from os.path    import join,exists
from os         import listdir
# Internal Modules
from dbgen.core.numeric                     import roundfloat
from dbgen.scripts.Pure.Atoms.json_to_traj  import json_to_traj

ForceTuple = Tuple[int,int,Optional[float],Optional[float],Optional[float]]
################################################################################
def get_traj_qe_lazy(a_l_p : Tuple[str,str,str])->List[Tuple[Atoms,int,float,List[ForceTuple],int]]:
    """
    Returns list of triples to represent the trajectory of a structure during
    an optimization. The ASE structure, the step number along the trajectory,
    and the energy. These are parsed from a Quantum Espresso log file.
    """
    anytraj,log,_ =a_l_p
    # Initialize
    #-----------
    output   = []
    CELL     = False
    POS      = False
    FORCE    = False
    cellvecs = [] # contains up to three entries like [0.000,1.15,16.324]
    atomdata = [] # contains many (SYMB,X,Y,Z) tuples
    forces   = []
    stepnum  = 0  # step in the trajectory
    traj  = json_to_traj(anytraj)

    # Constants
    #----------
    ryd_to_ev = 13.60569

    # Get log file
    #-------------
    lines = log.split('\n')
    for line in lines: # read lazily

        # MAIN LOOP
        #----------
        if 'crystal axes' in line:
            CELL = True
            cellvecs = []
        elif CELL and len(cellvecs)<3:
            try:
                cellvecs.append([roundfloat(x) for x in line.split()[3:6]])
            except ValueError:
                CELL = False
                cellvecs = []
            if 'a(3)' in line:
                CELL = False
        elif 'site n.' in line:
            POS = True
            atomdata = []
        elif 'number of atoms/cell' in line:
            num_atoms = int(line.split()[-1])
        elif POS:
            try:
                ind,sym,_,_,_,_,x,y,z,_ = line.split()
                remove_digits = str.maketrans('', '', digits)
                clean_symb = sym.translate(remove_digits)
                atomdata.append((clean_symb,(roundfloat(x),roundfloat(y),roundfloat(z))))
                if int(ind)== num_atoms:
                    POS = False
                    if cellvecs: # construct atoms if cell isn't malformed
                        atoms = Atoms(symbols = [a[0] for a in atomdata]
                                     ,positions = [a[1] for a in atomdata]
                                     ,cell = cellvecs
                                     ,constraint=traj.constraints
                                     ,tags=traj.get_tags())
                        atoms.wrap()
            except ValueError:
                POS = False
                atomdata = []
        elif 'total energy      ' in line:
            eng = float(line.split()[-2])
        elif  'smearing contrib' in line:
            ts = float(line.split()[-2])

        elif 'Forces acting' in line:
            FORCE = True
            forces = []

        elif FORCE and 'Total force' in line:
            FORCE = False
        elif FORCE and line.strip()!='' and 'rho' not in line:
            try:
                _,ind1,_,_,_,_,fx,fy,fz = line.split()
                forces.append((stepnum,int(ind1)-1,roundfloat(float(fx)* ryd_to_ev)
                                                  ,roundfloat(float(fy)* ryd_to_ev)
                                                  ,roundfloat(float(fz)* ryd_to_ev)))
            except ValueError:
                FORCE=False
                forces = []
        elif 'JOB DONE' in line:
            e = (eng-ts/2) * ryd_to_ev

            if all([cellvecs, atomdata , forces
                   , len(traj)==num_atoms
                   , len(traj)==len(forces)]):
                output.append((traj,stepnum,e,forces,0))
                stepnum += 1
                e = 0

    if forces: # premature end of file before job done
        e = (eng-ts/2) * ryd_to_ev
        output.append((atoms,stepnum,e,forces,1))


    output[-1] = tuple([*output[-1][:-1],1]) # set final for finaltraj
    return output
