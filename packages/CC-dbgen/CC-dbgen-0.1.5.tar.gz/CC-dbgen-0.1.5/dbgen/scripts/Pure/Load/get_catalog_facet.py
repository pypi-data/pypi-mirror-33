from typing import Tuple
from json import loads
def get_catalog_facet(paramdict:str)->Tuple[int,int,int]:
    """
    Extract facet from params.json
    """
    params = loads(paramdict)
    facet = params.get('facet')
    if facet is None:
        facet = params.get('facet_json')
        if facet is None:
            raise ValueError("Cannot find facet in params.json")
    return tuple(loads(facet))
