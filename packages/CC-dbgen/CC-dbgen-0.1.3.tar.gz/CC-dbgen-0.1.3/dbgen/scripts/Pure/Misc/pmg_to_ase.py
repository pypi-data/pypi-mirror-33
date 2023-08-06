from pymatgen import Structure  # type: ignore
from ase import Atoms  # type: ignore
from pymatgen.io.ase            import AseAtomsAdaptor      # type: ignore

def pmg_to_ase(pmg:Structure)->Atoms:
    """
    Convert a Pymatgen structure into an ASE atoms object
    """
    return AseAtomsAdaptor().get_atoms(pmg)
