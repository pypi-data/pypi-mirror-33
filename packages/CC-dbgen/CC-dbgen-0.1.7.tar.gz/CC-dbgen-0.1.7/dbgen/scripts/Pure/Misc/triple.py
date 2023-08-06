from typing import TypeVar, Tuple

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')

def triple(a : A
          ,b : B
          ,c : C
          ) -> Tuple[A,B,C] :
    """
    Three items into a tuple
    """
    return (a,b,c)
