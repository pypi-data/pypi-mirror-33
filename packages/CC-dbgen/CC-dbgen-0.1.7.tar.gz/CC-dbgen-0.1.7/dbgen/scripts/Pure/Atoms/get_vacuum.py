import numpy as np  # type: ignore
import ase          # type: ignore

def get_vacuum(atoms : ase.Atoms) -> float:
    """
    Same method as the one used in get_system_type.
    Assumes that z axis is normal to surface (would need PMG functions to
        reorient and make this function more robust)
    """
    c     = np.linalg.norm(atoms.get_cell()[2])
    delta = 0.0
    zs    = sorted([a.z for a in atoms])
    z     = zs[0]

    for z_next in zs:
        delta = max(delta, z_next - z)
        z = z_next

    return c - delta
