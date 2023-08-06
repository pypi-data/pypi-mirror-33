from typing import List,Tuple,Any

def unzip(x : List[Tuple[Any]])->Tuple[List[Any]]:
    """
    [(A,B,C,...)] -> ([A],[B],[C],...)
    """
    return tuple(map(list,zip(*x))) # type: ignore
