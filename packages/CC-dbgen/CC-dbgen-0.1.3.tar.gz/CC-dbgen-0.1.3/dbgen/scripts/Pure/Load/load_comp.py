from typing import Tuple,List

# External Modules
import json
from math      import gcd
from functools import reduce

# Internal Modules
from dbgen.core.lists import flatten

def load_comp(raw_structure : str
             ) -> Tuple[List[int],   List[int]
                           ,List[int],   List[int] , List[float]
                           ,List[float], List[int],  List[int]]:
    """
    Performs basic composition analysis, creating a row for every STRUCTURE x ELEMENT
    pair for which the element exists in the structure.

    Intended insert columns are:

              ['element_id',
               ,'count',	   	'count_fixed'
               ,'frac', 	   		'frac_fixed'
               ,'count_norm',  'count_fixed_norm']
    """

    # Load raw strings
    atomdata = json.loads(raw_structure)['atomdata']

    # Set up dictionaries of stoichiometries
    symbs     = [x['number'] for x in atomdata]
    setsymbs  = set(symbs)
    symbdict  = {s:symbs.count(s) for s in setsymbs}
    sum_      = sum(symbdict.values())
    denom     = reduce(gcd,symbdict.values(),0) # GCD of stoichiometry

    constsymbs = [x['number'] for x in atomdata if x['constrained']]
    fSymbdict = {s:constsymbs.count(s) for s in setsymbs}
    sumF = sum(fSymbdict.values())


    output = []
    for j in setsymbs:
        count       = symbdict[j]
        count_fixed = fSymbdict[j]

        frac        = round(count / sum_,3)
        frac_fixed  = 0 if sumF == 0 else round(count_fixed / sumF,3)

        count_norm = count/denom
        fixed_norm  = count_fixed/denom

        output.append((j,    count_fixed > 0
                      ,count,count_fixed,count_norm
                      ,frac, frac_fixed, fixed_norm))

    return list(map(list,zip(*output))) # type: ignore
