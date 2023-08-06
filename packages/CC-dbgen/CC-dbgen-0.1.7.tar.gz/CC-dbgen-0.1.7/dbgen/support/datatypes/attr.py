from typing import Optional,Any,List,TYPE_CHECKING
if TYPE_CHECKING:
    from dbgen.support.datatypes.object   import Object
from copy import deepcopy

from dbgen.support.datatypes.sqltypes   import SQLType,Int
from dbgen.support.datatypes.table      import Col
from dbgen.support.datatypes.constraint import EQ,NE,LT,GT
###############################################################################
class Attr():
    """
    A property of an object - needs a name and datatype
    Can be given a default value and NOT NULL constraint
    """
    def __init__(self
                ,name    : str
                ,dtype   : SQLType       = Int()
                ,nnull   : bool          = False
                ,ind     : bool          = False
                ,default : Optional[Any] = None
                ,uniq    : bool          = False
                ,auto    : bool          = False
                ,pk      : bool          = False
                ,obj     : str           = '???'
                ) -> None :

        self.name    = name
        self.dtype   = dtype
        self.nnull   = nnull
        self.ind     = ind
        self.default = default
        self.uniq    = uniq
        self.auto    = auto
        self.pk      = pk
        self.obj     = obj

    # Basic
    #------

    def __str__(self) -> str:
        return '%s.%s'%(self.obj,self.name)

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self,other : object)->EQ: # type: ignore
        return EQ(self,other)

    def __ne__(self,other : object)->NE: # type: ignore
        return NE(self,other)

    def __lt__(self,other : object)->LT: # type: ignore
        return LT(self,other)

    def __gt__(self,other : object)->GT: # type: ignore
        return GT(self,other)

    def __hash__(self)->int:
        return hash(self.name)

    # Other methods
    #--------------
    def _mkCol(self)->Col:
        return Col(name    = self.name
                  ,typ     = self.dtype
                  ,nn      = self.nnull
                  ,uniq    = self.uniq
                  ,ind     = self.ind
                  ,default = self.default
                  ,auto    = self.auto
                  ,pk      = self.pk)
