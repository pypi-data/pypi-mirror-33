from typing import Tuple,List,Dict
from networkx import MultiGraph                      # type: ignore
from networkx.algorithms import connected_components # type: ignore
from ase.data import chemical_symbols as symbs       # type: ignore
from pprint import pformat
def identify_ads(G:MultiGraph)->Tuple[List[int],List[int],List[str]
                                     ,List[int],List[str],List[str]]:
    """
    Returns [ATOM_INDEX] [ADSORBATE_ID] [NAME] triples (all lists of length M),
     followed by [ADSORBATE_ID] [NAME] [SITE] triples (all lists of length N < M)

    Atoms are considered to be adsorbates if they are in the set {H,O,C,N}
    These atoms are grouped by bonding and adsorbates are assigned arbitrary IDs
    THAT START AT 1 (Adsorbate ID = 0 means not an adsorbate in the atom table)
    """
    # Initialize Variables
    #--------------------
    ads_nodes = [] # type: List[int]
    adsnames  = []
    adssites  = []
    atomdata  = []
    m_bonds   = {} # type: Dict[int,int]
    ads_ind   = 1
    nonmetals = [1,4,6,7,8,9]
    has_metal = False # if we don't see any metal atoms, then there are no adsorbates (e.g. pure water structure)
                      # need to think about graphite / graphene cases
    # Constants
    #----------
    name_dict = {(1,):'H'
                ,(8,):'O'
                ,(7,):'N'
                ,(6,):'C'
                ,(8,8):'O2'
                ,(7,7):'N2'
                ,(6,6):'C2'
                ,(1,1):'H2'
                ,(1,7):'NH'
                ,(1,8):'OH'
                ,(1,1,7):'NH2'
                ,(1,1,1,7):'NH3'
                ,(1,7,7):'NNH'
                ,(1,1,7,7):'NNH2'
                ,(1,1,1,7,7):'NNH3'
                ,(1,1,8):'H2O'
                ,(6,8):'CO'
                ,(1,6,8):'CHO'
                ,(1,8,8):'OOH'
                ,(6,6,8,8):'OCCO'
                ,(1,6,6,8,8):'OCCHO'
                }
    site_dict = {1:'top'
                ,2:'bridge'
                ,3:'threefold'
                ,4:'fourfold'
                }
    # Create subgraph with only nonmetals (with 3 or fewer metal bonds)
    for i,data in G.nodes(data=True):
        if data['number'] in nonmetals:
            metal_bonds = 0
            for n in G.neighbors(i):
                if G.nodes[n]['number'] not in nonmetals:
                    metal_bonds+=1
            m_bonds[i] = metal_bonds
            if metal_bonds < 5:
                ads_nodes.append(i)
        else:
            has_metal = True
    if not has_metal:
        return [],[],[],[],[],[]
    else:

        ads = connected_components(G.subgraph(ads_nodes))
        for a in ads:
            elems = [G.nodes[n]['number'] for n in a]
            name  = name_dict.get(tuple(sorted(elems)))
            if name is not None:
                m_tot = sum(map(m_bonds.get,a)) # type: int
                site  = site_dict.get(m_tot,'other')
                adsnames.append(name)
                adssites.append(site)
                atomdata.extend([(G.nodes[n]['index'],ads_ind,name) for n in a])
                ads_ind+=1
            else:
                pass
                #print('could not find an adsorbate corresponding to '+pformat(elems))
            #summing number of metal bonds those atoms collectively have
        #import pdb;pdb.set_trace()
        if not atomdata:
            return [],[],[],[],[],[]
        else:
            inds,atom_ids,atom_names = tuple(map(list,zip(*atomdata)))
            ads_inds = list(range(1,len(adsnames)+1))
            return inds,atom_ids,atom_names,ads_inds,adsnames,adssites
