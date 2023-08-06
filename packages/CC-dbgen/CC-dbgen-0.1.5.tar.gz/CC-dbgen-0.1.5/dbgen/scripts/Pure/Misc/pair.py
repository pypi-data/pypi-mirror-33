from typing import TypeVar, Tuple

A = TypeVar('A')
B = TypeVar('B')

def pair(a : A
        ,b : B
        ) -> Tuple[A,B] :
    """Pairs two items into a tuple"""
    return (a,b)
