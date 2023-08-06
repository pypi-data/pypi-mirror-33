from networkx import node_link_data,MultiGraph # type: ignore
from json import dumps                         # type: ignore

def graph_to_json(G : MultiGraph)->str:
    """
    Serialize a MultiGraph
    """
    return dumps(node_link_data(G))
