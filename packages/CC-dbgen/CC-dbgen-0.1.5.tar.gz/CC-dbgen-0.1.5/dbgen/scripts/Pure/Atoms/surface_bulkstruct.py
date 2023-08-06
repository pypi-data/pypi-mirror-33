from typing                             import Tuple
from pymatgen.core.surface              import generate_all_slabs, SlabGenerator        # type: ignore
from pymatgen.symmetry.analyzer         import SpacegroupAnalyzer                       # type: ignore
from pymatgen                           import Lattice, Structure                       # type: ignore
from pymatgen.core.surface              import get_recp_symmetry_operation
from pymatgen.analysis.elasticity       import get_uvec                                 # type: ignore
from monty.fractions                    import gcd_float                                # type: ignore
from ase.io                             import read                                     # type: ignore
from pymatgen.io.ase                    import AseAtomsAdaptor                          # type: ignore
from ase                                import Atoms                                    # type: ignore
from ase.constraints import FixAtoms                                                    # type: ignore
import numpy as np                                                                      # type: ignore
from dbgen.core.lists import normalize_list

def surface_bulkstruct(atoms      : Atoms
                      ,resolution : float = 0.05
                      ,top_pad    : float = 5.0
                      ,symprec    : float = 0.2
                      ) -> Structure :
    """
    Drop the c lattice vector and look for highest symmetry structure, which is
    the representative of the bulk structure
    """
    print('starting surface bulkstruct with atoms = '+str(atoms))
    # helper class to break out of nested For loops
    #----------------------------------------------
    class BreakIt(Exception): pass

    # Identify constrained atoms
    #---------------------------
    fixed_inds = []
    if atoms.constraints:
        for constraint in atoms.constraints:
            if isinstance(constraint,FixAtoms):
                fixed_inds.extend(list(constraint.get_indices()))
    if fixed_inds==[]:
        fixed_inds = list(range(len(atoms)))

    # Only return structures with same composition as bulk
    #------------------------------------------------------
    comp_norm = sorted(normalize_list([x.number for x in atoms if x.index in fixed_inds]))

    # Initialize other variables
    #---------------------------
    highest_symmops,best_sgn,best_structure = 0,0,None
    slab       = AseAtomsAdaptor().get_structure(atoms)
    index_list = range(len(atoms))
    c_uvec     = get_uvec(slab.lattice.matrix[2])

    # Get unique c values to translate by
    #------------------------------------
    c_values = slab.frac_coords[:, 2].round(4)
    c_values = np.unique(c_values)
    c_values = sorted(c_values)
    c_values.pop(-1) # Probably don't need the top one

    for c_value in c_values: # for each atom

        # Translate sites so that this site is at the bottom of the cell
        #---------------------------------------------------------------
        test_struct = slab.copy()
        test_struct.translate_sites(index_list,[0,0,-c_value],to_unit_cell=False)

        # Remove all sites out of lower bound
        #------------------------------------
        above = lambda s: s.frac_coords[2] >= -0.0001
        test_struct = Structure.from_sites(list(filter(above,test_struct))) #[s for s in test_struct if s.frac_coords[2]>=-0.0001])

        # Resize lattice
        #---------------
        slab_c_mag = slab.lattice.c
        max_c_mag = slab_c_mag * np.max(test_struct.frac_coords[:, 2]) + top_pad # scale by max c coordinate
        c_mags = np.arange(2.0, max_c_mag, resolution).tolist()

        for c_mag in reversed(c_mags):
            new_matrix    = slab.lattice.matrix
            new_matrix[2] = c_uvec * c_mag
            new_lattice   = Lattice(new_matrix)

            # Cut off top
            #------------
            new_sites         = [s for s in test_struct if new_lattice.get_fractional_coords(s.coords)[2] < 1]
            inner_test_struct = Structure(new_lattice, [s.species_string for s in new_sites],
                                          [s.coords for s in new_sites], coords_are_cartesian=True)

            new_comp_norm = sorted(normalize_list(inner_test_struct.atomic_numbers))
            if new_comp_norm == comp_norm:
                try:
                    # Search for overlapping atoms
                    for i,a in enumerate(inner_test_struct):
                        if a.z < 0.3:
                            for j,b in enumerate(inner_test_struct):
                                if i!=j and a.distance(b)<0.3:
                                    raise BreakIt

                        # Test if new structure is the 'best' one seen so far
                        try:
                            sga = SpacegroupAnalyzer(inner_test_struct, symprec=symprec)
                            num_symmops = len(sga.get_symmetry_operations())
                            if len(sga.get_symmetry_operations()) > highest_symmops:
                                best_structure = inner_test_struct
                                highest_symmops = num_symmops
                                best_sgn        = sga.get_space_group_number()
                        except TypeError:
                            pass
                except BreakIt:
                    pass
    return best_structure

if __name__=='__main__':
    import sys
    a = read(sys.argv[1])
    print(surface_bulkstruct(a))
