from typing import Tuple,List,Dict
from gpaw import GPAW  #type: ignore
from gpaw.utilities import h2gpts #type: ignore
from ase.io import read,write     #type: ignore
from ase import Atoms,Atom       #type: ignore
from ase.units import Bohr   #type: ignore
import os
from string import ascii_uppercase,digits
from random import choices
from collections import defaultdict
import numpy as np   #type: ignore
from json import dumps


def quickgraph(atoms:Atoms)->str:
    calc = GPAW(mode='lcao',basis = 'dzp'
                    ,gpts          = h2gpts(0.15, atoms.get_cell(), idiv=8)
                    ,txt           = 'log'
                    ,fixdensity    = True
                    ,convergence   = {'energy':float('inf')
                                     ,'density':float('inf')})

    stordir = ''.join(choices(ascii_uppercase+digits, k=8))
    os.chdir(stordir)
    atoms.set_calculator(calc)
    atoms.get_potential_energy()
    density = calc.get_all_electron_density() * Bohr**3
    write(stordir+'/total_density.cube',atoms,data=density)
    job_control = '\n'.join(['<net charge>',"0.0","</net charge>"
                            ,"<periodicity along A, B, and C vectors>"
                            ,".true.",".true.",".true."
                            ,"</periodicity along A, B, and C vectors>"
                            ,'<compute BOs>','.true.','</compute BOs>'
                            ,'<atomic densities directory complete path>'
                            ,os.environ['CHARGEMOL_DENSITIES']
                            ,'</atomic densities directory complete path>'
                            ,'<charge type>','DDEC6','</charge type>'])

    os.system(os.environ['CHARGEMOL_BINARY'])

    ###############################################################
    def parse_line(line : str) -> Tuple[int,float,List[int]]:
        """
        Get bonded atom, bond order, and offset
        """
        assert line[:16]==' Bonded to the (', "No parse line ->"+line+'<- %d'%len(line)
        offStr,indStr,boStr = line[16:].split(')')
        offset = [int(x) for x in offStr.split(',')] # Chunk containing offset info
        ind    = int(indStr.split()[-3]) - 1        # Chunk containing index info (chargemol starts at 1, not 0)
        bo     = float(boStr.split()[4])            # Chunk containing B.O. info
        return (ind,bo,offset)

    class PotentialEdge(object):
        """
        Container for information we need to decide later if it's a
        graph-worthy bond. This class is nothing more than a dictionary.
        """
        def __init__(self
                    ,fromNode   : int
                    ,toNode     : int
                    ,bond_order : float
                    ,offset     : List[int]
                    ) -> None:

            self.fromNode = fromNode
            self.toNode   = toNode
            self.bondorder= bond_order
            self.pbc_x    = offset[0]
            self.pbc_y    = offset[1]
            self.pbc_z    = offset[2]


    class BondOrderSection(object):
        """
        Process one section of the Bond Order output of Chargemol
        """
        def __init__(self
                    ,ind       : int
                    ,raw_lines : List[str]
                    ,pbcdict   : dict
                    ) -> None:

            self.ind      = ind
            self.bonds    = [parse_line(x) for x in raw_lines]
            self.pbcdict  = pbcdict

        def _relative_shift(self
                           ,i : int
                           ,j : int
                           ) -> np.array:
            """
            Given a pbc_dict and two indices, return the original pbc shift
            for a bond from i to j
            """
            pi,pj = [np.array(self.pbcdict[x]) for x in [i,j]]
            return pj - pi

        def makeEdge(self
                    ,tup :  Tuple[int,float,List[int]]
                    ) -> PotentialEdge:
            """
            Creates an Edge instance from the result of a parsed Bond Order log line
            """
            (toInd,bo,offset) = tup
            fromInd = self.ind

            # correct for WRAPPING atoms
            offset = (np.array(offset) +  self._relative_shift(fromInd,toInd)).tolist()

            shift = np.dot(offset, atoms.get_cell()) # PBC shift
            p1    = atoms[fromInd].position
            p2    = atoms[toInd].position + shift
            d     = np.linalg.norm(p2-p1)
            return PotentialEdge(fromInd,toInd,bo,offset)

        def make_edges(self)->List[PotentialEdge]:
            """Apply edgemaker to result of parsing logfile lines"""
            return  [self.makeEdge(b) for b in self.bonds]



    def mk_pbc_dict(atoms : Atoms
                   ) -> Dict[int,Tuple[int,int,int]]:
        """
        Helpful docstring
        """
        def g(tup : tuple)->Tuple[int,int,int]:
            """
            Helper function to yield tuples for pbc_dict
            """
            def f(x : float)->int:
                """
                Helper function for g
                """
                if   x < 0: return -1
                elif x < 1: return 0
                else:       return 1

            x,y,z = tup
            return (f(x),f(y),f(z))

        scaled_pos  = atoms.get_scaled_positions(wrap=False).tolist()
        scaled_pos_ = zip(range(len(atoms)),scaled_pos)
        pbc_dict    = {i : g(p) for i,p in scaled_pos_}
        return pbc_dict

    def parse_chargemol_pbc(header_lines : List[str]
                           ,cell         : List[float]
                           ) -> Dict[int,Tuple[int,int,int]]:
        """
        Helpful docstring
        """
        atoms = Atoms(cell=cell)

        for i,l in enumerate(header_lines[2:]):
            try:
                if '*' in l:
                    l = l.replace('*','') + ' ???' #Asterisks are touching the z value
                s,x,y,z,_ = l.split()
                p = [float(q) for q in [x,y,z]]
                atoms.append(Atom(s,position=p))
            except Exception as e:
                pass #print('exception???',e)

        return mk_pbc_dict(atoms)
    def dict_diff(d1 : Dict[int,np.array]
                 ,d2 : Dict[int,np.array]
                 ) -> Dict[int,np.array]:
        """
        Helpful docstring
        """
        return {i: np.array(d2[i]) - np.array(d1[i]) for i in d1.keys()}


    header,content    = [], [] # type: Tuple[List[str],List[str]]
    sections          = []     # type: List[BondOrderSection]
    head_flag,counter = True,-1       # Initialize
    filepath = stordir+'/DDEC6_even_tempered_bond_orders.xyz' # File to parse

    pbcdict = mk_pbc_dict(atoms) # the 'true' PBC coordinate of each atom

    filtedges = []
    with open(filepath,'r') as f:
        for line in f:
            if not (line.isspace() or line[:4] == ' 201'): # remove blank lines and calendar date
                if line[1]=='=':
                    head_flag = False                                            # no longer in header  section
                    chargemol_pbc = parse_chargemol_pbc(header,atoms.get_cell()) # PBC of chargemol atoms

                elif head_flag: header.append(line)     # we're still in the header section
                elif 'Printing' in line:                # we're describing a new atom
                    content = []                        # reset buffer content
                    counter += 1                        # update index of our from_index atom
                elif 'sum' in line:                     # summary line at end of a section
                    dic = dict_diff(pbcdict,chargemol_pbc)
                    edgs = BondOrderSection(counter,content,dic).make_edges()
                    filtedges.extend([e for e in edgs
                        if  (e.bondorder > 0.04) and (e.fromNode <= e.toNode)])
                else:
                    content.append(line)              # business-as-usual, add to buffer

    return dumps([e.__dict__.values() for e in filtedges])

if __name__ == '__main__':
    a = read('~/dbgen/data/suncatdata/ksb/150792226224/init.traj')
    print(quickgraph(a))
