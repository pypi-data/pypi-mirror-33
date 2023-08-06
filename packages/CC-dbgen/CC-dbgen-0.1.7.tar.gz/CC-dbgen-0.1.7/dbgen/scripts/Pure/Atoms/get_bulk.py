from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ase import Atoms # type: ignore
from ase.io import write,read # type: ignore
from bulk_enumerator.bulk import BULK # type: ignore
from os import remove
from string import ascii_uppercase,digits
from random import choices

def get_bulk(atoms : 'Atoms'
            ,tol   : float  = 0.05
            ) -> BULK:
    """
    Create a BULK object from Ankit's library
    """
    # Constants
    #----------
    pth = ''.join(choices(ascii_uppercase+digits, k=16))+'_POSCAR'
    # Initialize
    #-----------
    assert tol <= 0.1 # requirement?
    b = BULK(tolerance=tol)
    poscar = ''
    # Get POSCAR String
    #------------------
    while poscar == '':
        write(pth,atoms,format='vasp')
        try:
            with open(pth,'r') as f:
                poscar = f.read()
        except IOError:
            pass # try repeatedly

    # Create bulk from POSCAR string
    #-------------------------------
    b.set_structure_from_file(poscar)

    if b.get_name()=='':
        raise ValueError('problem with getting bulk: \n'+poscar)
    try:
        remove(pth)
    except IOError:
        pass

    return b
