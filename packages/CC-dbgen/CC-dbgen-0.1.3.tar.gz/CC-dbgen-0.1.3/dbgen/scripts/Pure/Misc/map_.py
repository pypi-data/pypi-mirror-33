from typing import TypeVar,Callable,List
A = TypeVar('A')
B = TypeVar('B')

def map_(f    : Callable[[A],B]
        ,args : List[A]
        ) -> List[B]:
    """
    Maps a function over an input. If each input has multiple outputs, than
    multiple lists are generated.
    """
    mapped = [f(arg) for arg in args]

    if mapped == []:
        return []
    else:
        if not isinstance(mapped[0],tuple):
            return mapped
        else:
            return tuple(map(list,zip(*mapped)))
