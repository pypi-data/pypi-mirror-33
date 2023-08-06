#External Modules
from typing import List,TYPE_CHECKING
if TYPE_CHECKING:
    from dbgen.support.datatypes.object     import Schema

from abc    import abstractmethod
#Internal Modules
from dbgen.support.datatypes.attr       import Attr
from dbgen.support.datatypes.metatemp   import Block
from dbgen.support.datatypes.misc       import noIndex
from dbgen.support.utils                import addQs
################################################################################

class InsertUpdate(object):
    @abstractmethod
    def mk_block(self)->Block:
        raise NotImplementedError

class Insert(InsertUpdate):
    """
    Take items in a namespace and store them as attributes on objects
    in the database
    """
    def __init__(self
                ,schema : 'Schema'
                ,attrs  : List[Attr]
                ) -> None:
        self.obj = schema.get_(attrs[0].obj)
        assert all([a.obj == self.obj._name for a in attrs])
        self.attrs = attrs
        self.n     = len(attrs)

    def mk_block(self)->Block:
        colnames = [a.name for a in self.attrs]
        qs       = ','.join(['%s']*self.n)
        name     = 'insert_%s_%s'%(self.obj._name,','.join(colnames))
        text     = 'INSERT INTO %s (%s) VALUES (%s)'%(self.obj._name
                                                   ,','.join(colnames)
                                                   ,qs)
        dup      = ' ON DUPLICATE KEY UPDATE {0} = {0}'.format(colnames[0])
        args = noIndex(colnames)
        return Block(name = name
                    ,text = text + dup
                    ,args = args)


class Update(InsertUpdate):
    """
    Update attributes of an object
    """
    def __init__(self
                ,schema : 'Schema'
                ,attrs : List[Attr]
                ) -> None:
        self.schema = schema
        self.obj = schema.get_(attrs[0].obj)
        assert all([a.obj == self.obj._name for a in attrs])
        self.attrs = attrs

    def mk_block(self)->Block:
        colnames = [a.name for a in self.attrs]
        pk_cols  = [a.name for a in self.obj._pks(self.schema)]
        name     = 'update_%s_%s'%(self.obj._name,','.join(colnames))
        setstr   = addQs(colnames,',')
        where    = addQs(pk_cols,' AND ')
        text     = 'UPDATE %s SET %s WHERE %s'%(self.obj._name,setstr,where)
        args = noIndex(colnames+pk_cols)
        return Block(name = name
                    ,text = text
                    ,args = args)
