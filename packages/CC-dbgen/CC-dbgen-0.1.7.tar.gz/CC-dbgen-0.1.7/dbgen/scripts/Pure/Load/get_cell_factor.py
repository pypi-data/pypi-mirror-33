from typing import Dict,Optional

from dbgen.core.parsing import parse_line

def get_cell_factor(pwinp : str
                   ,dftcode : str
                   ) -> Optional[float]:
    """
    Get cell factor for vc relax jobs
    """
    if dftcode !='quantumespresso':
        return None

    line  = parse_line(pwinp,'cell_factor=')
    if line is None:
        return None
    else:
        raw = line.replace('d','=').split('=')[1]
        return float(raw)

if __name__=='__main__':
    # Test on a QE pw.inp file
    import sys
    with open(sys.argv[1],'r') as f:
        print(get_cell_factor(f.read(),'quantumespresso'))
