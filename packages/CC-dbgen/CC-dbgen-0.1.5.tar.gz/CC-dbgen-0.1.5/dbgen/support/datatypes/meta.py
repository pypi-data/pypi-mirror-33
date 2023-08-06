#External
from typing import Dict,Any,Tuple,Union,Set,List
# Internal
from dbgen.support.datatypes.sqltypes   import SQLType,Int,Varchar,Text,Decimal
from dbgen.support.datatypes.attr         import Attr



#############################################################################
# Constants
class NotNull(object): pass
NOTNULL = NotNull()

class DEFAULT(object):
    def __init__(self,val:Any)->None:
        self.val = val
################################################################################
################################################################################
################################################################################

class Object(object):
    """
    Superclass for user-defined objects (which correspond to DB tables)

    _parents
        -- SUFFICIENT and NECCESARY objects needed to specify an instance
          (e.g. for 'Atom', 'Struct' and 'Element' (+ 'atom_id')
           are both necessary, but Struct+atom_id are sufficient.
    _components
        --
    <not starting with '_'>
        -- normal attribute
    """
    universe = {}    # type: Dict[str,Object]
    todo     = set() # type: Set[str]

    def __init_subclass__(cls      : 'Object'  # type: ignore
                         ,**kwargs : dict
                         ) -> None:
        """
        Upgrade a user-defined class given the state of the universe
        """
        if kwargs:
            raise ValueError('kwargs? '+str(kwargs))
        else:
            self._init_subclass(cls)

    @staticmethod
    def _init_subclass(cls:'Object')->None:
        uni  = cls.universe          # type: ignore
        todo = cls.todo              # type: ignore
        name = cls.__name__.lower()  # type: ignore
        if name in uni:
            print('Warning: this class was already defined for this universe')
            return None # No repeats allowed
        else:
            cd              = cls.__dict__
            parents         = cd.get('_parents',[])
            cls._parents    = parents
            components      = cd.get('_components',[])
            cls._components = components
            many_to_one     = cd.get('_many_to_one',False)
            cls._many_to_one= many_to_one
            cls._attrs      = [cls.mkAttr(k,v) for k,v in cd.items() if k[0]!='_']
            for a in cls._attrs:
                setattr(cls,a.name,a)

            cls._pks = [] # type: List[Attr]

            if ((not parents) or many_to_one):
                cls._pks.append(Attr(name+'_id',pk=True,auto=True))


            for p in parents:
                assert isinstance(p,(Object,str))
                if isinstance(p,Object) or p.lower() in uni:
                    if isinstance(p,Object): parent = p
                    else: parent = uni[p.lower()]

                    cls._process_parent(parent)


                else:
                    todo.add(p.lower())
            #import pdb;pdb.set_trace()
            uni[name] = cls
            if name in todo:
                todo.remove(name)

    def _process_parent(self,par:'Object')->None:
        print('processing parent of '+str(self))
        print('par is '+str(par))
        pass

    def __init__(self,alias:str)->None:
        self.alias=alias

    @staticmethod
    def mkAttr(name:str,data:Union[SQLType,Tuple])->Attr:
        if isinstance(data,tuple):
            types = (SQLType,NotNull,DEFAULT)
            assert all([isinstance(x,types) for x in data])
            dtype = [d for d in data if isinstance(d,SQLType)][0]
            return Attr(name,dtype=dtype,nnull=NOTNULL in data)
        else:
            return Attr(name,dtype=data)
################################################################################
################################################################################
################################################################################
class Structure(Object):
    """
    Chemical structure defined in periodic cell
    """
    raw     = Text(),NOTNULL

class Element(Object):
    """
    Chemical element
    """
    mass    = Decimal(),NOTNULL

class Atom(Object):
    """
    An atom in a specific chemical structure
    """
    _parents    = [Structure]
    _components = [Element]
    x           =  Decimal(),NOTNULL
    y           =  Decimal(),NOTNULL
    z           =  Decimal(),NOTNULL



a1 = Atom('1')
a2 = Atom('2')

import pdb;pdb.set_trace()
