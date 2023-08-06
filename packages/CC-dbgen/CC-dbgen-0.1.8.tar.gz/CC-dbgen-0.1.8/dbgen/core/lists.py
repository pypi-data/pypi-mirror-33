from typing import Any, List, Callable, TypeVar, Dict,Iterable
A = TypeVar('A')
B = TypeVar('B')

################################################################################


def gcd(args: List[Any])->Any:
    """
    Greatest common denominator of a list
    """
    if len(args) == 1:
        return args[0]
    L = list(args)
    while len(L) > 1:
        a, b = L[len(L) - 2], L[len(L) - 1]
        L = L[:len(L) - 2]
        while a:
            a, b = b % a, a
        L.append(b)
    return abs(b)


def flatten(lol: List[List[A]])->List[A]:
    """Convert list of lists to a single list via concatenation"""
    return [item for sublist in lol for item in sublist]


def merge_dicts(dicts: List[Dict[A, B]])->Dict[A, B]:
    return {k: v for d in dicts for k, v in d.items()}


def concat_map(f: Callable[[A], List[B]], args: List[A]
               ) -> List[B]:
    """
    Maps a function over an input.
    We apply the function to every element in the list and concatenate result.

    """
    return flatten([f(arg) for arg in args])


def normalize_list(l: list) -> list:
    """
    [a,a,a,a,b,b,c,c] => [a,a,b,c]
    """
    if len(l) == 0:
        return l
    d = {x: l.count(x) for x in l}
    div = gcd(list(d.values()))
    norm = [[k] * (v // div) for k, v in d.items()]
    return [item for sublist in norm for item in sublist]
