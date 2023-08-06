from typing import Tuple
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer       # type: ignore
import numpy as np                                              # type: ignore
from pymatgen import Lattice,Structure                          # type: ignore
from pymatgen.core.surface import get_recp_symmetry_operation   # type: ignore
from monty.fractions import gcd_float                           # type: ignore
from ase.visualize                      import view             # type: ignore
from pymatgen.io.ase                    import AseAtomsAdaptor  # type: ignore


def get_miller(structure:Structure)->Tuple[int,int,int]:
    """
    Courtesy of Joey M.
    """
    # Get normal uvec
    normal = np.cross(structure.lattice.matrix[0], structure.lattice.matrix[1])
    normal /= np.linalg.norm(normal)

    # Get the conventional lattice in the same basis as the current structure
    sga = SpacegroupAnalyzer(structure,symprec=0.15)
    trans_mat = sga.get_symmetry_dataset()['transformation_matrix']
    conv_latt = Lattice(np.transpose(np.dot(np.transpose(
                structure.lattice.matrix), np.linalg.inv(trans_mat))))

    # Convert to frac coords, then normalize to gcd
    normal_in_frac = conv_latt.get_fractional_coords(normal)
    miller = np.array([v if abs(v) > 1e-8 else 0 for v in normal_in_frac])
    miller /= abs(gcd_float([m for m in miller if not np.isclose(m, 0)]))
    miller = miller.round(5)

    # If you really want, you can do this thing and it'll sort all of the
    # equivalent miller indices and give the last one in a sort by value
    recip_symmops = get_recp_symmetry_operation(sga.get_conventional_standard_structure())
    equiv_millers = [tuple([int(x) for x in op.operate(miller)]) for op in recip_symmops]
    miller = sorted(equiv_millers)[-1]

    return miller

if __name__=='__main__':
    import sys
    from ase.io import read # type: ignore
    from dbgen.scripts.Pure.Atoms.surface_bulkstruct import surface_bulkstruct  # type: ignore
    pth = sys.argv[1]
    print(get_miller(surface_bulkstruct(read(pth))))
