from typing import List,Dict
from  ase  import Atoms                         # type: ignore
from ase.constraints import FixAtoms            # type: ignore
import networkx as nx                           # type: ignore
import numpy as np                              # type: ignore
from scipy.cluster.hierarchy import fclusterdata #type: ignore
from json import loads
from collections import defaultdict

def mk_graph(atoms        : 'Atoms'
            ,include_frac : float
            ,group_cut    : float
            ,min_bo       : float
            ,bonddata     : str
            ,bothways     : bool       = False
            ) -> nx.MultiGraph:
    """
    Create a graph
    Bonddata is a json'd list of tuples containing the following Edge information
        (fromNode  : int
        ,toNode    : int
        ,bondorder : float
        ,x         : int
        ,y         : int
        ,z         : int)
    """

    # Auxillary Functions
    #--------------------
    def make_adjacency_matrix(es : List[dict])->List[List[float]]:
        """
        Square matrix where (i,j) is the sum of bond order between atoms i and j
        """
        output = np.zeros((len(atoms),len(atoms)))   # type: ignore
        for edge in es:
            output[edge['fromNode'],edge['toNode']] += edge['bondorder']
        return output.tolist()

    def make_group(edge_list:List[dict])->List[List[dict]]:
        """
        Partitions a set of Edges into groups with similar bond strength
        """

        # Handle edge cases
        #==================
        if len(edge_list)==0:  return []
        if len(edge_list)==1:  return [edge_list]

        strs = np.array([[e['bondorder'] for e in edge_list]]).T # create (n_edges,1) array
        groups = defaultdict(list)  #type: dict

        group_inds = list(fclusterdata(strs,group_cut
                                ,criterion='distance',method='ward'))

        for i in range(len(edge_list)): groups[group_inds[i]].append(edge_list[i])
        maxbo_groups = [(max([e['bondorder'] for e in es]),es) for es in groups.values()]
        sorted_maxbo_groups = list(reversed(sorted(maxbo_groups)))
        return [es for maxbo,es in sorted_maxbo_groups]

    def get_filtered_edges(bonds : List[dict])->List[dict]:
        if bonds == []: return [] # (no) edge case
        output = [] # type: List[dict]
        edge_dict = defaultdict(list) # type: Dict[int,List[dict]]
        for bond in bonds:
            edge_dict[bond['fromNode']].append(bond)

        total_bo = {ind:sum([e['bondorder'] for e in es])
                            for ind,es in edge_dict.items()}
        groups   = {ind: make_group(es)
                            for ind,es in edge_dict.items()}

        max_ind  = max([max(e['fromNode'], e['toNode']) for e in bonds])

        for ind in groups.keys():
            if total_bo[ind] > 0:
                accumulated = 0.0
                for i, group in enumerate(groups[ind]):
                    output.extend(group)
                    accumulated += sum([e['bondorder'] for e in group])/total_bo[ind]
                    if accumulated > include_frac:
                        break
        return output

    # Main Program
    #--------------
    attrs = ['toNode','fromNode','bondorder','x','y','z']
    if bonddata == '[]':
        bonds = [] # type: List[dict]
    else:
        bonds = [dict(zip(attrs,args)) for args in loads(bonddata)]
        if bothways:
            for b in bonds:
                if b['fromNode'] <= b['fromNode']:
                    bonds.append(dict(zip(attrs,(b['toNode']
                                     ,b['fromNode']
                                     ,b['bondorder']
                                     ,-b['x'],-b['y'],-b['z']))))

    G  = nx.MultiGraph(cell = atoms.get_cell().tolist())  # Initialize graph

    fixed_inds = []
    if atoms.constraints:
        for constraint in atoms.constraints:
            if isinstance(constraint,FixAtoms):
                fixed_inds.extend(list(constraint.get_indices()))

    for i in range(len(atoms)): # add nodes
        G.add_node(i,symbol      = atoms[i].symbol
                    ,number      = int(atoms[i].number)
                    ,position    = atoms[i].position.tolist()
                    ,index       = i
                    ,constrained = int(i in fixed_inds)
                    ,magmom      = atoms[i].magmom)

        edges = get_filtered_edges(bonds)

    for e in edges:
        prop_dict = {'bondorder':e['bondorder']
                    ,'pbc_shift': (e['x'],e['y'],e['z'])}
        tupl = (e['toNode'],e['fromNode'])
        G.add_edges_from([tupl],**prop_dict)

    adj_matrix = make_adjacency_matrix(edges)

    G.graph['adj_matrix'] = adj_matrix

    return G
