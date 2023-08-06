from typing import Callable,TypeVar,Optional
from  ase import Atoms # type: ignore
from glob import glob
from ase.io import read # type: ignore
from os.path import join,exists,getsize
from numpy.linalg import norm # type: ignore
from numpy import vectorize   # type: ignore

"""
Miscellaneous Core Functions / Objects

higher order
    maybe
    cast_maybe
    identity

numeric
    roundfloat

IO
    anytraj

Strings
    levenshteinDistance
"""

################################################################################
# Higher order functions
#------------------
X = TypeVar('X')
Y = TypeVar('Y')
def maybe(f : Callable[[X],Y]
         ) -> Callable[[Optional[X]]
                          ,Optional[Y]]:
    """
    Lift a unary function (that might normally fail on a None input)
        such that it only applies the function if the argument is not None
        (returns None if it is)
    """
    def g(x : Optional[X])->Optional[Y]:
        if x is None:
            return None
        else:
            return f(x)
    return g

# Dict[str,Callable]
cast_maybe = {'int':  maybe(int)  # type: ignore
              ,'bool': maybe(lambda x: 1 if '.TRUE.' in x else 0) # type: ignore
              ,'str' : maybe(lambda x: x)  # type: ignore
              ,'float': maybe(float) # type: ignore
              }

T = TypeVar('T')
def identity(x:T)->T:
    return x # type: ignore

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')

def compose(x : A
           ,f : Callable[[A],B]  = identity
           ,g : Callable[[B],C]  = identity
           ) -> C:
    return g(f(x))
################################################################################
################################################################################
def anytraj(root : str
            ) -> Atoms:
    """
    ASE IO read function - takes any traj it can find
    """
    qn = join(root,'qn.traj')
    if exists(qn) and getsize(qn) > 100:
        return read(qn)
    trajs = glob(join(root,'*.traj'))
    if len(trajs)==0:
        raise ValueError('Get Traj could not find any traj in '+root)
    else:
        return read(trajs[0])

def wrap(atoms:Atoms)->Atoms:
    mags = [norm(x) for x in atoms.get_cell()]
    def wrap_coord(coord:float,cell_len:float)->float:
        if coord < 0: coord+=cell_len
        elif coord > cell_len: coord-=cell_len
        return coord
    for i in range(len(atoms)):
        for j in range(3):

            atoms.positions[i][j] = wrap_coord(atoms.positions[i][j],mags[j]) # atoms.positions[i][j] =
            if atoms.positions[i][j] < 0:
                import pdb;pdb.set_trace()
    return atoms
################################################################################
################################################################################

def levenshteinDistance(s1 : str, s2 : str) -> int:
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = list(range(len(s1) + 1))
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]
