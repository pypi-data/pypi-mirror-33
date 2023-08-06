from typing import List,Tuple
from networkx import MultiGraph,Graph  # type: ignore

def layers(MG:MultiGraph)->Tuple[List[int],List[int]]:
    """
    Assign constrained atoms as 'layer 0'.
    Atoms within one edge of layer n are labeled as layer n+1.
    """
    G = Graph(MG.copy()) # we don't care about multiple edges for this
    layer_dict = {d['index']:0 for _,d in G.nodes(data=True) if d['constrained']}
    curr_layer = 0
    if not layer_dict:
        return [],[]
    else:
        while len(layer_dict) < len(G):
            curr_atoms = [x for x in range(len(G)) if layer_dict.get(x) == curr_layer]
            for a in curr_atoms:
                for e in G.neighbors(a):
                    if e not in layer_dict:
                        layer_dict[e]=curr_layer+1
            curr_layer+=1
            if curr_layer > 50:
                for i in range(len(G)):
                    if i not in layer_dict:
                        layer_dict[i]=None
                break

        return list(layer_dict.keys()),list(layer_dict.values())

if __name__=='__main__':
    from dbgen.main                               import realDB
    from dbgen.support.utils                      import sqlselect
    from dbgen.scripts.Pure.Graph.json_to_graph   import json_to_graph
    import sys
    q = """SELECT geo_graph
            FROM alljob JOIN finaltraj USING (job_id)
                        JOIN struct USING (struct_id)
            WHERE  stordir = %s"""
    gstr = sqlselect(realDB,q,[sys.argv[1]])[0][0]
    G = json_to_graph(gstr)
    print(layers(G))
