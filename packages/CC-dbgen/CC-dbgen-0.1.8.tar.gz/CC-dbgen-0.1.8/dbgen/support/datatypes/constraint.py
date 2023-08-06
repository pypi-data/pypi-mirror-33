from typing import Any,TYPE_CHECKING,Set
from abc    import abstractmethod
if TYPE_CHECKING:
    from dbgen.support.datatypes.attr import Attr
    # from dbgen.support.datatypes.object import _Object

################################################################################
class Constraint(object):
    def __init__(self)->None: pass

    def __repr__(self)->str:
        return 'Constraint(%s)'%(str(self))

    @abstractmethod
    def attrs(self)->Set['Attr']:
        raise NotImplementedError
################################################################################
class UnaryConstraint(Constraint):
    def __init__(self,obj:Any)->None:
        self.obj = obj
    def attrs(self)->Set['Attr']:
        """
        Avoid Cyclic
        """
        from dbgen.support.datatypes.object import Attr
        return set([self.obj]) if isinstance(self.obj,Attr) else set()
class NOT(UnaryConstraint):
    def __init__(self,obj:Any)->None:
        super().__init__(obj)
    def __str__(self)->str:
        return "NOT %s"%self.obj

class NULL(UnaryConstraint):
    def __init__(self,obj:Any)->None:
        super().__init__(obj)
    def __str__(self)->str:
        return "%s IS NULL"%self.obj

class IN(UnaryConstraint):
    def __init__(self,obj:Any,lst:list)->None:
        super().__init__(obj)
        self.lst = lst
    def __str__(self)->str:
        return "%s IN (%s)"%(self.obj,','.join(map(str,self.lst)))

################################################################################
class BinaryConstraint(Constraint):
    def __init__(self,o1:Any,o2:Any)->None:
        self.o1 = o1
        self.o2 = o2

    def attrs(self)->Set['Attr']:
        from dbgen.support.datatypes.object import Attr
        s1 = set([self.o1]) if isinstance(self.o1,Attr) else set()
        s2 = set([self.o2]) if isinstance(self.o2,Attr) else set()
        return s1 | s2

class EQ(BinaryConstraint):
    def __init__(self,o1:Any,o2:Any)->None:
        super().__init__(o1,o2)

    def __str__(self)->str:
        return '%s = %s'%(self.o1,self.o2)

class NE(BinaryConstraint):
    def __init__(self,o1:Any,o2:Any)->None:
        super().__init__(o1,o2)

    def __str__(self)->str:
        return '%s != %s'%(self.o1,self.o2)

class LT(BinaryConstraint):
    def __init__(self,o1:Any,o2:Any)->None:
        super().__init__(o1,o2)

    def __str__(self)->str:
        return '%s < %s'%(self.o1,self.o2)

class GT(BinaryConstraint):
    def __init__(self,o1:Any,o2:Any)->None:
        super().__init__(o1,o2)

    def __str__(self)->str:
        return '%s > %s'%(self.o1,self.o2)
# #####################
# def HAS(o:'_Object',comp:'_Object')->UnaryConstraint:
#     return NOT(HASNT(o,comp))
#
# def HASNT(o:'_Object',comp:'_Object')->UnaryConstraint:
#     for fk in o.fks:
#         if fk._to == comp:
#             return NULL(fk.from_attr[0])
#     raise ValueError
