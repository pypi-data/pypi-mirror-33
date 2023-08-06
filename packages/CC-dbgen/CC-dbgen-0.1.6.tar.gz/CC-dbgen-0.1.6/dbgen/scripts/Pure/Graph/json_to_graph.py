from networkx import node_link_graph,MultiGraph # type: ignore
from json import loads

def json_to_graph(raw : str) -> MultiGraph:
    """
    Deserialize a MultiGraph
    """
    return node_link_graph(loads(raw))

if __name__=='__main__':
    from dbgen.main import realDB
    from dbgen.support.utils import sqlselect
    import sys
    q = """SELECT geo_graph
            FROM alljob JOIN finaltraj USING (job_id)
                        JOIN struct USING (struct_id)
            WHERE  stordir = %s"""
    gstr = sqlselect(realDB,q,[sys.argv[1]])[0][0]
    G = json_to_graph(gstr)
