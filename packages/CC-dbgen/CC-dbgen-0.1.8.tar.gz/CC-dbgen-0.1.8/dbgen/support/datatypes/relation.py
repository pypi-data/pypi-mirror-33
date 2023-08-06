#External Modules
from typing import Callable,List,Optional,Union,Dict
#Internal Modules
from dbgen.support.datatypes.select         import Select
from dbgen.support.datatypes.temp           import Temp,TempFunc,Const
from dbgen.support.datatypes.insertupdate   import InsertUpdate

from dbgen.support.datatypes.rule       import Rule
from dbgen.support.datatypes.metatemp   import MetaTemp
from dbgen.support.datatypes.misc       import Arg

################################################################################

class Relation(object):
    """
    Relate attributes of objects via triples of:
    -select:  Extracting info from the current state of the world
    -func:    User-defined data-processing pipeline
    -inserts: putting information back into the DB
    """
    def __init__(self
                ,name      : str
                ,select    : Optional[Select]   = None
                ,func      : Temp               = Temp()
                ,inserts   : List[InsertUpdate] = []
                ) -> None:
        self.name    = name
        self.select  = select
        self.func    = func
        self.inserts = inserts
    def mk_rule(self)->Rule:
        return Rule(name     = self.name
                   ,query    = str(self.select) if self.select else None
                   ,template = self.func
                   ,metatemp = MetaTemp([iu.mk_block() for iu in self.inserts]))
