from typing import Dict,Optional,Union
from dbgen.core.parsing import parse_line
from dbgen.core.misc    import cast_maybe

def get_vasp_key(dftcode : str
                ,outcar   : str
                ,key     : str
                ,dtype   : str
                ) -> Optional[Union[int,str,float]]:
    """
    common form of extracting VASP input info not present in QE/GPAW jobs

    If looking for a bool and key not found (e.g. LUSE_VDW), return False by default
    """

    assert dtype in cast_maybe.keys(), 'bad dtype argument for get_vasp_key: '+dtype

    if dftcode =='vasp':
        parsed = parse_line(outcar,key.upper(),0)
        if parsed is None:
            if dtype=='bool':
                return 0
            else:
                return None
        else:
            val = parsed.split('=')[-1].strip().split()[0]
            return cast_maybe[dtype](val) # type: ignore
    else:
        return None
