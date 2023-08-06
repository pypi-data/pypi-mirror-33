from typing import List,Tuple
import json
import os

################################################################################

def parse_mendeleev()->Tuple[List[int],List[int],List[str]
                                ,List[float],List[int],List[str]]:
    """
    Extracts information of elements
    """
    rootpath = os.environ['DBGEN_ROOT']

    with open(os.path.join(rootpath,'data/element.json'),'r') as f:
        elems = json.load(f)
    ############################
    cols = ['atomic_number','atomic_weight','spacegroup','pointgroup'] # etc

    allcols = ['atomic_number', 'symbol', 'name', 'atomic_weight','atomic_radius'
              , 'phase','evaporation_heat', 'pointgroup','spacegroup'
              , 'melting_point', 'metallic_radius', 'vdw_radius'
              , 'density', 'en_allen' , 'is_radioactive'
              , 'lattice_structure' , 'fusion_heat'
              , 'econf', 'period', 'covalent_radius_bragg'
              , 'geochemical_class', 'abundance_crust', 'heat_of_formation'
              , 'electron_affinity', 'atomic_volume',  'boiling_point'
              , 'proton_affinity', 'covalent_radius_slater'
              , 'lattice_constant', 'dipole_polarizability'
              , 'en_ghosh', 'thermal_conductivity', 'group_id', 'en_pauling'
              , 'gas_basicity'
              ,'abundance_sea']

    output = []
    for e in elems:
        output.append([e.get(k) for k in allcols])

    return tuple(map(list,zip(*output))) # type: ignore
