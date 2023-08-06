from typing import List,FrozenSet
from dbgen.support.datatypes.relation   import Relation
from dbgen.support.datatypes.object     import Object,Schema
from dbgen.support.datatypes.func       import Func
from dbgen.support.datatypes.dbg        import DBG
from dbgen.support.datatypes.misc       import ConnectInfo

################################################################################
class Model(object):
    def __init__(self
                ,schema   : Schema
                ,relations : List[Relation]
                ) -> None:
        self.schema    = schema
        self.relations = relations
        self.objects   = schema.objects

    def createDBG(self)->DBG:
        tables = [o._mkTable(self.schema) for o in self.objects]
        rules  = [r.mk_rule() for r in self.relations]
        return DBG(tables=tables,rules=rules)

    def run(self
           ,reset   : bool = False
           ,catalog : bool = False
           ) -> None:
        db = ConnectInfo()
        x  = set() if catalog else {'catalog'}
        self.createDBG().run_all(db,reset=reset,xclude=x,parallel=False)
