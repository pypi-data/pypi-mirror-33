# External Modules
from typing      import List,Optional,Dict,FrozenSet,Set,Tuple
from pprint      import pformat
from copy        import deepcopy
from abc         import abstractmethod
from collections import defaultdict,OrderedDict
from networkx    import DiGraph                                 # type: ignore
from networkx.algorithms.simple_paths import all_simple_paths   # type: ignore
from networkx.algorithms.dag          import descendants        # type: ignore
from networkx.algorithms              import simple_cycles      # type: ignore

# Internal modules
from dbgen.core.lists                     import flatten
from dbgen.support.datatypes.attr         import Attr
from dbgen.support.datatypes.table        import Table,FK as OldFK
from dbgen.support.datatypes.constraint   import EQ,NE,LT,GT,Constraint
from dbgen.support.datatypes.insertupdate import Insert,Update

"""
Defines the FK, Object, Join, From, and Universe classes
"""

class Object(object):
    """
    parent      - What is this object defined by? If nothing, it gets its own
                  independent ID, otherwise it requires IDs of parents to be constructed
    attr        - Simple attributes of the object (int/text/float)
    uniqattr    - List of attr names which should have UNIQUE constraint applied
    many_to_one - indicates a many-one relationship with parents

    Current Problems
        - cannot put a not null constraint on component FK
            (specify 'necessary component')
    """
    def __init__(self
                ,name        : str
                ,desc        : str
                ,parents     : List[str]  = []
                ,components  : List[str]  = []
                ,attr        : List[Attr] = []
                ,uniqattr    : List[str]  = []
                ,many_to_one : bool       = False
                ) -> None :

        self._name        = name
        self._desc        = desc
        self._parents     = parents
        self._components  = components
        self._many_to_one = many_to_one

        # Handle attributes
        #------------------
        attrs = []
        for a in attr:
            assert a.name[0] != '_' # no collisions with internal fields
            a.obj = self._name
            if a.name in uniqattr:
                a.uniq = True
            attrs.append(a)
            setattr(self,a.name,a)

        self._attr = attrs

        # Integrity checks
        #-----------------
        if many_to_one:
            assert len(parents) > 0

    # Basic Methods
    #--------------
    def __str__(self) -> str:
        return 'Object(%s)'%(self._name)

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self,other : object)->bool:
        if isinstance(other,Object):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __hash__(self)->int:
        return hash(self._name)
    #
    # # Other Methods
    # #--------------
    # def get(self,attr : str)->Optional[Attr]:
    #     """
    #     Safe access of attributes
    #     """
    #     for a in self._attr:
    #         if a.name == attr:
    #             return a
    #     return None
    #
    # def get_unsafe(self,attr:str)->Attr:
    #     x = self.get(attr)
    #
    #     if x is None:
    #         msg = "Called getUnsafe when Attr %s not present in Object %s"
    #         raise ValueError(msg%(attr,self._name))
    #     else:
    #         return x
    #
    # def select(self
    #           ,schema : 'Schema'
    #           ,attrs  : Optional[List[str]] = None
    #           ) -> List[Attr]:
    #     if attrs is None:
    #         return self._pks(schema)
    #     else:
    #         return list(filter(None,map(self.get,attrs)))
    #
    # def _pks(self,schema:'Schema')->List[Attr]:
    #     """
    #     Return a list of Attr that are PKs as well as any related FK objects
    #
    #     Keep the data associated with parent PKs excpet:
    #         - change the owner
    #         - prefix the name with the table it came from
    #         - remove the autoincrement
    #     """
    #     # Create key for this object (not needed if completely dependent)
    #     if self._many_to_one:
    #         ks = [Attr(name=self._name+'_id',pk=True,auto=True,obj=self._alias)]
    #     else:
    #         ks = []
    #
    #     return ks + self._pkfks(schema)
    #
    # def _pkfks(self,schema:'Schema')->List[Attr]:
    #     pkfks = []
    #     for p in schema.get(self._parents):
    #         for k in p._pks(schema):
    #             k.auto = False
    #             k.name = k.obj+'_'+k.name
    #             k.obj  = self._alias
    #             pkfks.append(k)
    #     return pkfks
    #
    # def _fks(self,schema:'Schema')->List['FK']:
    #     FKs = []
    #     for comp in schema.get(self._components):
    #         colnames = [comp._name+'_'+c.name for c in comp._pks(schema)]
    #         _fks     = []
    #         for cn in colnames:
    #             fk = Attr(cn)
    #             fk.obj = self._alias
    #             _fks.append(fk)
    #             setattr(self,cn,fk)
    #         FKs.append(FK(self,_fks,comp,comp._pks(schema)))
    #     return FKs
    #
    # def _fk_attrs(self,schema:'Schema')->List[Attr]:
    #     """Get the from_attr from all of an Object's FKs (so that we can create
    #     the Columns)"""
    #     return flatten([fk.from_attr for fk in self._fks(schema)])
    #
    # def As(self,alias:str)->'Object':
    #     """
    #     Create identical object but with different alias
    #     """
    #     new = deepcopy(self)
    #     new._alias +='_'+alias
    #     return new
    #
    # def _mkTable(self,schema:'Schema')->Table:
    #     cols = flatten([list(x) for x in [self._attr
    #                                      ,self._pks(schema)
    #                                      ,self._fk_attrs(schema)]])
    #     return Table(name = self._name
    #                 ,desc = self._desc
    #                 ,cols = [c._mkCol() for c in cols]
    #                 ,fks  = [fk.to_old_style() for fk in self._fks(schema)])
    #
    # def insert(self
    #           ,schema    : 'Schema'
    #           ,attr_list : Optional[List[str]] = None
    #           ) -> Insert:
    #     if attr_list is None:
    #         return Insert(schema,self._pks(schema))
    #     else:
    #         try:
    #             return Insert(schema,[self.get_unsafe(x) for x in attr_list])
    #         except ValueError as e:
    #             print(e)
    #             import pdb;pdb.set_trace()
    #             raise ValueError
    #
    # def update(self,schema:'Schema',attr_list:List[str])->Update:
    #     return Update(schema,[self.get_unsafe(x) for x in attr_list])
    #
    # def update_component(self
    #                     ,schema : 'Schema'
    #                     ,o      : 'Object'
    #                     ) -> Update:
    #     fks = [fk for fk in self._fks(schema) if fk._to == o]
    #     assert len(fks)==1
    #     return Update(schema,fks[0].from_attr)


################################################################################
class FK(object):
    """
    A Foreign Key in the language of Objects/Attributes is a pair of lists of
    Attributes, each having equal length but referring to different Objects
    """
    def __init__(self
                ,from_attr : List['Attr']
                ,_to       : '_Object'
                ,to_attr   : List['Attr']
                ) -> None:
        # Validate
        #---------
        err1 = 'FK args not of equal length: %s %s'
        assert len(from_attr) == len(to_attr), err1%(from_attr,to_attr)
        err2 = 'FK args share the same object: %s'
        assert from_attr[0].obj != to_attr[0].obj, err2%from_attr[0].obj

        # Store Fields
        #-------------

        self.from_attr = from_attr
        self._to       = _to
        self.to_attr   = to_attr

    def flip(self,_from:'_Object') -> None:
        temp_attr       = self.from_attr
        self.from_attr  = self.to_attr
        self.to_attr    = temp_attr
        self._to        = _from

    def zipped(self) -> str:
        z = zip(self.from_attr,self.to_attr)
        return ' AND '.join(['%s = %s'%(f,t) for f,t in z])

    def to_old_style(self) -> OldFK:
        if self.to_attr[0].obj is None:
            raise ValueError
        else:
            return OldFK([a.name for a in self.from_attr]
                         ,self._to.name
                         ,[a.name for a in self.to_attr])

################################################################################

class _Object(object):
    def __init__(self
                ,name        : str
                ,desc        : str
                ,parents     : List[_Object]  = []
                ,components  : List[_Object]  = []
                ,attr        : List[Attr]     = []
                ,pks         : List[Attr]     = []
                ,fks         : List[FK]       = []
                ,fks_to      : List[FK]       = []
                ,many_to_one : bool           = False
                ) -> None :
        self.name        = name
        self.desc        = desc
        self.parents     = parents
        self.components  = components
        self.attr        = attr
        self.pks         = pks
        self.fks         = fks
        self.fks_to      = fks_to
        self.many_to_one = many_to_one

        # Validate
        #---------
        assert set(pks).issubset(attr)

class Universe(object):
    """
    Unordered, immutable collection of Objects
    """
    def __init__(self,objects:List[Object])->None:
        self.objects   = frozenset(objects)
        self.obj_dict  = {o._name : o for o in objects}
        self.pk_dict   = {} # type: Dict[str,List[Attr]]
        self._obj_dict = {} # type: Dict[str,_Object]
        self._obj_dict = {n:self.upgrade(n) for n in [o._name for o in objects]}
        self._objects  = frozenset(self._obj_dict.values())
        self.graph     = self.mk_graph()
        import pdb;pdb.set_trace()

    def get_pks(self,obj_str:str)->List[Attr]:
        if obj_str in self.pk_dict:
            return self.pk_dict[obj_str]
        else:
            obj = self.obj_dict[obj_str]
            a0  = Attr(name=obj_str+'_id',pk=True,auto=True,obj=obj._name)
            pks = [a0] if (obj._many_to_one or (not obj._parents)) else []
            for p in obj._parents:
                new_pks = [Attr(p+'_'+k.name,obj=obj._name)
                            for k in self.get_pks(p)]
                pks.extend(new_pks)
            return pks

    def upgrade(self,o_str:str)->_Object:
        """
        In light of a fixed Universe, compute richer properties of each Object
        (recursively with memoization)
        """
        if o_str in self._obj_dict: return self._obj_dict[o_str]

        # Get primary keys (recursively, with memoization)
        pks = self.get_pks(o_str)

        o = self.obj_dict[o_str]

        # Get Foreign Keys from this object to its components
        fks = []
        for comp in o._components + o._parents:
            colnames = [comp + '_' + c.name for c in self.get_pks(comp)]
            _fks     = [Attr(cn,obj=o_str) for cn in colnames]
            fks.append(FK(_fks,self.upgrade(comp),self.get_pks(comp)))

        # Get the columns associated with foreign keys from this object
        fk_attrs = flatten([fk.from_attr for fk in fks])

        # Assemble all the information
        _object = _Object(name     = o_str
                      ,desc        = o._desc
                      ,parents     = [self.upgrade(x) for x in o._parents]
                      ,components  = [self.upgrade(x) for x in o._components]
                      ,attr        = self.get_pks(o_str) + fk_attrs + o._attr
                      ,pks         = pks
                      ,fks         = fks
                      ,many_to_one = o._many_to_one)
        self._obj_dict[o_str] = _object
        return _object

    def mk_graph(self)->DiGraph:
        """
        Given parent/component relationships between objects, create a Directed
        Graph that captures the possible flows of information.
        """
        G = DiGraph()
        G.add_nodes_from([o._name for o in self.objects])
        for o1 in self.objects:
            if not o1._many_to_one:
                for o2 in o1._parents:
                    G.add_edge(o2,o1._name)
            for o2 in o1._parents + o1._components:
                    G.add_edge(o1._name,o2)
        return G

    def path(self,o:str,o2:str)->List[List[str]]:
        """
        All possible paths between two objects via FK propagation
        """
        paths = all_simple_paths(self.mk_graph(),o,o2)
        return sorted(list(paths),key=len)

    def get_fk(self,o1:_Object,o2:_Object)->FK:
        """
        Gets a FK between two Objects -- error if more/fewer are found
        """
        fks = [fk for fk in o1.fks if fk._to is o2]  + [fk for fk in o2.fks if fk._to is o1]
        if len(fks) > 1:
            print('Too many fks between %s and %s: %s'%(o1,o2,fks))
            import pdb;pdb.set_trace()
            raise ValueError
        elif len(fks) == 0:
            print('No many fks between %s and %s'%(o1,o2))
            import pdb;pdb.set_trace()
            raise ValueError
        else:
            fk = fks[0]
            if fk._to != o2:
                fk.flip(o1)
            return fk

    def get(self,obj_str:List[str])->List[_Object]:
        return [self.get_(x) for x in obj_str]

    def get_(self,obj_str:str)->_Object:
        return self._obj_dict[obj_str]

    def select(self
              ,attrs       : List[Attr]
              ,constraints : List[Constraint] = []
              ,maybeNull   : List[Object]     = []
              ) -> str:
        allobj    = self.get(sorted(set([a.obj for a in attrs])))
        pk_attrs  = flatten([o.pks for o in allobj])

        # Make from
        cols   = '\n\t,'.join([str(a) for a in attrs])
        consts = '\n\tAND '.join([str(c) for c in constraints])
        c_attrs = flatten([list(c.attrs()) for c in constraints])

        all_attr = attrs + c_attrs
        _from = self.mkFrom(all_attr)

        for j in _from.joins:
            if j.fk._to in maybeNull:
                j.kind = "LEFT"

        return 'SELECT %s\n%s\nWHERE %s'%(cols,_from,consts or '1')

    def mkFrom(self,attrs:List[Attr])->From:
        """
        Construct a FROM clause that joins the right tables in order to get
        access to a set of attributes mentioned by some query
        """
        objects  = self.get([a.obj for a in attrs])

        found    = False
        for obj in objects:
            desc = descendants(self.graph,obj.name)
            if all([o.name in desc for o in objects if o != obj]):
                found = True
                first = obj

        if not found:
            raise ValueError('You screwed up')

        joins = []
        for o in objects:
            if o != first:
                paths = self.path(first.name,o.name)
                if len(paths)>1:
                    print("Warning, more than one path found between %s and %s"%(first,o))
                path = paths[0]
                assert path[0] == first.name
                curr_obj = first # initialize with this

                for s in path[1:]: # first element = first._name
                    next_obj = self._obj_dict[s]
                    fk = self.get_fk(curr_obj,next_obj)
                    joins.append(Join(next_obj,fk))
                    curr_obj = next_obj

        return From(first,joins)
#
#
#
class From(object):
    """
    FROM clause
    """
    def __init__(self
                ,obj   : _Object
                ,joins : List[Join] = []
                ) -> None:
        self.obj   = obj
        self.joins = joins

    # Basic Methods
    #--------------
    def __str__(self) -> str:
        raise NotImplementedError
        return 'FROM %s AS %s '%(self.obj._name,self.obj._name) + ''.join(['\n%s'%j for j in self.joins])

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self,other : object)->bool:
        if isinstance(other,Object):
            return self.__dict__ == other.__dict__
        else:
            return False


class Join(object):
    """
    JOIN <A> AS <B> ON <C> = <D> AND ...
    """
    def __init__(self
                ,obj  : _Object
                ,fk   : FK
                ,kind : str     = 'INNER'
                ) -> None:
        self.obj  = obj
        self.fk   = fk
        self.kind = kind
    # Basic Methods
    #--------------
    def __str__(self) -> str:
        join   = '%s JOIN'%self.kind
        to_obj = self.fk._to
        if to_obj is None:
            raise ValueError
        else:
            tab    = '%s AS %s'%(to_obj.name,to_obj.name)
            return '\n\t%s %s \n\t\tON %s'%(join,tab,self.fk.zipped())
