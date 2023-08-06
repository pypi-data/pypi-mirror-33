from typing import List,Tuple,TYPE_CHECKING
if TYPE_CHECKING:
    from ase import Atoms # type: ignore
from pymatgen.io.ase 			import AseAtomsAdaptor 	         # type: ignore
from pymatgen.analysis.structure_analyzer import VoronoiAnalyzer # type: ignore

def get_voronoi(atoms:'Atoms')->Tuple[List[int],List[int],List[int],List[int]
                                 ,List[int],List[int],List[int],List[int]
                                 ,List[int]]:
    """
    Voronoi analysis returns # of 3-10 sided polyhedra. Error yields -1 values.
    """
    pmg = AseAtomsAdaptor().get_structure(atoms)
    inds = list(range(len(atoms)))
    try:
        out = [[i,*VoronoiAnalyzer().analyze(pmg,i)] for i in inds]
        return tuple(map(list,zip(*out)))  # type: ignore
    except:
        return tuple([inds] + [[-1]*len(atoms)]*8)   # type: ignore
