from typing import Dict,Optional

from dbgen.core.parsing import parse_line

def get_cell_dofree(pwinp   : str
                   ,dftcode : str
                   ) -> Optional[str]:
    """
    Get cell degrees of freedom for vc relax jobs
    """
    if dftcode !='quantumespresso':
        return None

    line  = parse_line(pwinp,"cell_dofree='")
    if line is None:
        return None
    else:
        raw = line.split("'")[1]
        return raw

if __name__=='__main__':
    # Test on a QE pw.inp file
    import sys
    with open(sys.argv[1],'r') as f:
        print(get_cell_dofree(f.read(),'quantumespresso'))
