from typing import Tuple,List
from json import loads
from dbgen.core.lists import flatten

def get_catalog_ads(jsonads:str)->Tuple[List[int],List[int]]:
    """
    Analyzes params.json's "adsorbates" field
    """
    if not jsonads:
        return ([],[])
    else:
        ads = loads(jsonads)
        if not ads or ads==[[]]:
            return ([],[])
        output = [[(i,a) for a in ad] for i,ad in enumerate(ads)]
        try:
            ads,inds = zip(*flatten(output))
        except:
            import pdb;pdb.set_trace()
        return list(ads),list(inds)
