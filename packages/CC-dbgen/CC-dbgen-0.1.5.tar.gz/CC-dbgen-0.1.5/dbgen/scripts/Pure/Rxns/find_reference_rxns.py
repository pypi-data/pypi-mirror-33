from typing import Optional,List,Dict,Tuple
from json import loads,dumps
import numpy as np             # type: ignore
from numpy.linalg import solve # type: ignore

from dbgen.core.lists import flatten
from dbgen.core.numeric import common_integer

def find_reference_rxns(job     : int
                       ,job_ref : int
                       ,stoich  : str
                       ,refdata : Optional[str]
                       ) -> Tuple[str
                                    ,List[int]
                                    ,List[int]]:
    """
    Return a list of rxn names followed by unzipped <rxn,job,coef> triples
    We trust that the reference system will not have linearly dependent entries
    so we can just solve an Ax=b matrix problem where each row of A is a stoich
    vector of a reference, and b column is the stoich vector of the target job.

    If the input job is itself a reference, then we're in a tricky situation.
    We want to be able to query the reaction and find that its formation energy
    is zero, so there are two intuitive reactions to log: A (stoich 1) and A (stoich -1)
    or just A (stoich 0) If we did the first one, then that violates the PK
    constraint on job_id of stoich table, so we opt for the second strategy.

    """
    no_output = ('dummy',[],[]) # type: Tuple[str,List[int],List[int]]

    #####################
    # Auxillary Functions
    #--------------------
    def dict_to_vector(d     : Dict[int,int]
                      ,basis : List[int]
                      ) -> np.array:
        return np.array([d.get(b,0) for b in basis])

    def rxn_namer(out : List[Tuple[int,int]])->str:
        """This could definitely be improved to give coherent rxn names
          , though they'll still need to have job numbers since many different
          'rxns' have the same stoichiometry
          """
        return dumps(sorted(out))

    ##############
    # Main Program
    ##############

    # Process input strings
    #---------------------
    if refdata is None:
        return no_output
    elif job_ref > 0:
        return str(job),[job],[0]


    stoichdict = dict(loads(stoich))                     # {element : count}
    targetkeys = set(stoichdict.keys())
    allrefs    = [(a,b,dict(c)) for a,b,c in loads(refdata)] # [(JobID,{ElemID:Count})]
    refs       = [(a,b,c) for a,b,c in allrefs if not set(c.keys()).isdisjoint(targetkeys)]
    if refs == []:
        return no_output
    allelems   = list( targetkeys
                      | set(flatten([list(c.keys()) for _,_,c in refs])))

    # If multiple refs are for the same element, pick one at random
    # Later we'll try to do something better where multiple reactions are
    # output to accommodate all possibilities
    stoichmap = {x[1] : x for x in refs}

    uniqrefs  = list(stoichmap.values())

    # Set up matrices to solve for linear combination of references
    b = dict_to_vector(stoichdict,allelems)
    b = b.reshape(len(allelems),1)
    A = np.concatenate([dict_to_vector(r,allelems) for _,_,r in uniqrefs],axis=0)

    A.resize(len(allelems),len(allelems)) # make a square matrix, pad with zeros

    try:
        coef_array = solve(A,b)
    except:
        return no_output
    coefs = flatten(coef_array.tolist())


    output_ids = [job]+[uniqrefs[i][0] for i,coef in enumerate(coefs) if coef != 0]
    output_coefs = [-1.0]+coefs
    normed_coefs = common_integer(output_coefs)
    print('\t\tnormed %s to %s'%(output_coefs,normed_coefs))

    name = rxn_namer(list(zip(output_ids,normed_coefs)))
    print('named %s to %s'%(list(zip(output_ids,normed_coefs)),name))
    return name,output_ids,normed_coefs # type: ignore
