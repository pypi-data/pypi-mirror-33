from typing import TypeVar,Callable,List
A = TypeVar('A')
B = TypeVar('B')

from dbgen.core.lists import flatten


def concat_map(f : Callable[[A],List[B]]
              ,args:List[A]
              ) -> List[B]:
    """
    Maps a function over an input. Function is expected to return ([a],[b],...)
    We apply the function to every element in the list and concatenate each tuple
    element.

    """
    mapped = [f(arg) for arg in args]

    if mapped == []:
        return []
    elif isinstance(mapped[0],list):
        return flatten(mapped)
    elif isinstance(mapped[0],tuple):
        example = list(zip(*mapped))
        return tuple(map(flatten,zip(*mapped)))
    else:
        raise ValueError('did you mean to use concat_map?',mapped)
