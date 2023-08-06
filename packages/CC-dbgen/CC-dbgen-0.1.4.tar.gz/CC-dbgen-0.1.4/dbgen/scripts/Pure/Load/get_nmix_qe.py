from typing import Dict,Optional
from dbgen.core.parsing import parse_line

def get_nmix_qe(log   : str
            ) -> Optional[float]:
    """
    Need a better solution eventually, some log files don't have mixing_ndim?
    """

    parsed = parse_line(log,'number of iterations used')
    if parsed is None:
        raise ValueError('Malformed QE logfile? cannot find "number of iterations used"')
    else:
        raw    = parsed.split("=")[1].strip().split()[0]
        return int(raw)
