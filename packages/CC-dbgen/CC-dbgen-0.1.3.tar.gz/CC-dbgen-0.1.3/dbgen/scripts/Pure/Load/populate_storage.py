from typing import Tuple,List
from os     import environ
def populate_storage()->Tuple[List[str],List[str],List[str]]:
    """
    Reads DFT_LOGFILES to find a structured textfile with information
    about what directories should be considered 'roots'
    """
    with open(environ['DFT_LOGFILES'],'r') as f:
        rootdata  = [l.split() for l in f.readlines() if '#' not in l and l.strip()!='']
    paths,codes,labels = zip(*rootdata)
    return list(paths),list(codes),list(labels)
