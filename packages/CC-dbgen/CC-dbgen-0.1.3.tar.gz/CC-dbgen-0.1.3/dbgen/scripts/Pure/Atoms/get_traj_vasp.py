from typing import Dict,List,Tuple,Optional
from re import compile,VERBOSE
from ase import Atoms # type: ignore
from os.path import join,exists

from dbgen.core.parsing import parse_line,btw
from dbgen.core.numeric import roundfloat
from dbgen.core.lists   import flatten


ForceTuple = Tuple[int,int,Optional[float],Optional[float],Optional[float]]

def get_traj_vasp(stordir : str)->List[Tuple[Atoms,int,float,List[ForceTuple],int]]:
    """
    Returns list of quadruples to represent the trajectory of a structure during
    an optimization.
        - ASE structure,
        - the step number along the trajectory,
        - the energy
        - the forces.

    These are parsed from VASP's OUTCAR and POSCAR.
    """

    # Prequel: extract the list of chemical symbols from POSCAR in a convoluted way
    #-----------------------------------------------------------------------------
    with open(join(stordir,'POSCAR'),'r') as f: plines = f.readlines()
    uniqsymbs = plines[0].split() # ['H','O','Na']
    quantities = plines[5].split() # ['2','1','5']
    symbs = flatten([[a]*int(b) for a,b in zip(uniqsymbs,quantities)]) # ['H','H','O','Na','Na','Na','Na','Na']

    # Auxillary Functions
    #-------------------
    def l2vec(l:str)->list:
        """The first three numbers of a cell line contain x,y,z information"""
        return [roundfloat(x) for x in l.split()[:3]]

    def l2force(step:int,ind:int,l:str)->tuple:
        """
        The last three lines of a force line contain fx,fy,fz information
        A 'force' tuple needs the step number and atom number in its tuple, too
        """
        _,_,_,fx,fy,fz = l.split()
        return (step,ind,roundfloat(fx),roundfloat(fy) ,roundfloat(fz))

    def parse_v_section(sect    : str
                       ,stepnum : int
                       ) -> Tuple[Atoms
                                  ,int
                                  ,float
                                  ,List[ForceTuple]
                                  ,int]:
        """
        For a single ionic step, make a tuple with (Atoms,stepnum,energy,forces)
        """
        cell_text,cell_ind = btw(sect
                                 ,'reciprocal lattice vectors'
                                 ,'length of vectors')

        celllines = cell_text.split('\n')[1:-2]
        cell      = [l2vec(x) for x in celllines] # 3x3 matrix-like thing


        pf_text,pf_ind  = btw(sect
                             ,'POSITION'
                             ,'total drift'
                             ,cell_ind)

        lines       = pf_text.split('\n')[2:-2]
        posforces   = [(l2vec(x),l2force(stepnum,i,x)) for i,x in enumerate(lines)]
        pos,forces  = zip(*posforces)

        atoms  = Atoms(symbols   = symbs
                      ,positions = pos # <number of atoms> x 3 matrix thing
                      ,cell      = cell)

        atoms.wrap()
        eng = float(parse_line(sect[pf_ind:],'energy\(sigma->0\)',-1).split()[-1]) # "energy\(sigma->0\) = -73.2442"

        assert len(forces)==len(atoms), 'bad parsing of forces ... probably? (%d != %d)'%(len(forces),len(atoms))

        return (atoms,stepnum,eng,forces,0)

    # MAIN PROGRAM
    #-------------
    with open(join(stordir,'OUTCAR'),'r') as f: outcar = f.read()
    sections = outcar.split('EDIFF is reached')[1:]

    output = [parse_v_section(x,n) for n,x in enumerate(sections)]
    output[-1] = tuple([*output[-1][:-1],1]) # set final for finaltraj
    return output
