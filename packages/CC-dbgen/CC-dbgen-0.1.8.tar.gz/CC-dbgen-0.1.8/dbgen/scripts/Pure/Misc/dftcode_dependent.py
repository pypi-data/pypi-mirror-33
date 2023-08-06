from typing import TypeVar,Callable
A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')
D = TypeVar('D')

from dbgen.core.misc import identity
################################################################################
def dftcode_dependent(dftcode      : str
                     ,raw_input    : A
                     ,gpaw_func    : Callable[[B],C]
                     ,qe_func      : Callable[[B],C]
                     ,vasp_func    : Callable[[B],C]
                     ,pre_process  : Callable[[A],B] = identity
                     ,post_process : Callable[[C],D] = identity
                     ) -> D:
    """
    Higher order function for common paradigm: three completely different
    functions needed depending on DFT code
    """
    input = pre_process(raw_input)

    if dftcode == 'gpaw':
        raw_output =  gpaw_func(input)
    elif dftcode == 'quantumespresso':
        raw_output =  qe_func(input)
    elif dftcode == 'vasp':
        raw_output =  vasp_func(input)
    else:
        raise NotImplementedError('No implementation for dftcode ',dftcode)


    return post_process(raw_output)
