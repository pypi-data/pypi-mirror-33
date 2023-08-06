from typing import Dict,List,Tuple,Optional
from ase import Atoms # type: ignore
from string import digits
from os.path import join,exists
from os import listdir

from dbgen.core.parsing import parse_line,btw
from dbgen.core.numeric import roundfloat
from dbgen.core.lists   import flatten

ForceTuple = Tuple[int,int,Optional[float],Optional[float],Optional[float]]

def get_traj(stordir:str)->List[Tuple[Atoms,int,float,List[ForceTuple],int]]:
    """
    Returns list of triples to represent the trajectory of a structure during
    an optimization. The ASE structure, the step number along the trajectory,
    and the energy. These are parsed from a Quantum Espresso log file.
    """

    # Constants
    ryd_to_ev = 13.60569

    def mkAtom(rawatom : str) -> Tuple[str,Tuple[float,float,float]]:
        _,sym,_,_,_,_,x,y,z,_ = rawatom.split()
        remove_digits = str.maketrans('', '', digits)
        clean_symb = sym.translate(remove_digits)
        return (clean_symb,(roundfloat(x),roundfloat(y),roundfloat(z)))

    def parse_cell_line(l : str) -> List[float]:
        return [roundfloat(x) for x in l.split()[3:-1]]

    def parse_force_line(step : int
                        ,l    : str
                        ) -> ForceTuple:
        _,ind1,_,_,_,_,fx,fy,fz = l.split()
        return (step,int(ind1)-1,float(fx)* ryd_to_ev,float(fy)* ryd_to_ev,float(fz)* ryd_to_ev)

    def parse_section(sect    : str
                     ,stepnum : int
                     ) -> Tuple[Atoms,int,float,List[ForceTuple]]:

        cell_text,cell_ind = btw(sect,'crystal axes:','reciprocal')
        cell_lines = cell_text.strip().split('\n')[1:]
        cell = [parse_cell_line(x) for x in cell_lines[:3]]

        a_text,a_ind  = btw(sect,"site n.","number of k points",cell_ind)
        rawatoms = a_text.strip().split('\n')[1:]
        allatoms = list(map(mkAtom,rawatoms))
        atoms    = Atoms(symbols   = [a[0] for a in allatoms]
                        ,positions = [a[1] for a in allatoms]
                        ,cell      = cell)
        atoms.wrap()


        eng_line = parse_line(sect[a_ind:],'total energy',0)
        ts_line  = parse_line(sect[a_ind:],'smearing contrib',-1)
        if eng_line is None:
            for line in reversed(sect.split('\n')):
                if 'total energy' in line:
                    eng_line = line
                elif 'smearing contrib' in line:
                    ts_line = line

        e        = float(eng_line.split()[-2])
        ts       = float(ts_line.split()[-2])
        ev_eng   = (e-ts/2) * ryd_to_ev

        end_pattern = 'Total force' if 'Total force' in sect[a_ind:] else '$'
        f_text,_ =  btw(sect,'Forces acting on',end_pattern,a_ind)
        force_lines = f_text.strip().split('\n')[2:]


        forces = [parse_force_line(stepnum,x) for x in force_lines
                if len(x.split())==9 and 'force =' in x]


        if len(forces)!=len(atoms):
            forces = [(stepnum,i,None,None,None) for i in range(len(atoms))]

        return (atoms,stepnum,ev_eng,forces,0)


    # Main program
    #--------------

    # Get log file
    #-------------
    if exists(join(stordir,'log')):
        log = join(stordir,'log')
    else:
        for subdir in listdir(stordir):
            if exists(join(stordir,subdir,'log')):
                log = join(stordir,subdir,'log')
    with open(log,'r') as f: logfile = f.read()

    sections = logfile.split('JOB DONE') # re.split('JOB DONE',
    if len(sections)>5:
        sections = sections[-5:]
    output = [parse_section(x,n) for n,x in enumerate(sections)
                if 'total energy' in x and 'reciprocal' in x] # sometimes there are malformed sections that are missing key pieces of info ... discard them? HACK

    output[-1] = tuple([*output[-1][:-1],1]) # set final for finaltraj
    return output
