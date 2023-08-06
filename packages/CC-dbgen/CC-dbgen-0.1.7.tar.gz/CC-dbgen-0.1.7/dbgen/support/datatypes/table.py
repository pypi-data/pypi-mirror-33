# External Modules
from typing import Optional,List,Union,Any,Tuple,Set
from pprint import pformat
# Internal Modules
from dbgen.support.sqlparsing         import parse_dependencies
from dbgen.support.utils              import sqlite_select,sqlite_execute,mkInsCmd,namespaceCmd,get_tab_id
from dbgen.support.datatypes.sqltypes import SQLType,Int

"""
Defines Table, Col, FK, and View

"""

################################################################################
getColCmd  = """SELECT col.col_id FROM tab
                JOIN col USING (tab_id)
                WHERE tab.tab_id = ? AND col.name = ? """
################################################################################

class Table(object):
    """
    - Tables are used to collect information about a class of entities/objects
    """
    def __init__(self
                ,name  : str
                ,desc  : Optional[str]  = 'No description'
                ,cols  : List['Col']     = []
                ,fks   : List['FK']     = []
                ) -> None:
        assert any([x.pk for x in cols]), "need at least one primary key column for "+name
        self.name = name
        self.cols = self.mkFKcols(cols,fks)
        self.desc = desc
        self.fks  = fks

    def src(self)->str:
        cols = '\n\t\t,'.join([c.src() for c in self.cols])
        fks = '\n\t,fks = [%s]'%'\n\t\t,'.join([fk.src() for fk in self.fks]) if self.fks else ''
        return "Table('{0}'\n\t,desc=\"\"\"{1}\"\"\"\n\t,cols=[{2}]{3})".format(self.name,self.desc,cols,fks)

    def __str__(self)->str:
        return pformat(self.__dict__)
    def __repr__(self)->str:
        return str(self)
    def __eq__(self,other : object)->bool:
        return self.__dict__==other.__dict__

    @staticmethod
    def mkFKcols(cols : List['Col']
                ,fks  : List['FK']
                ) -> List['Col']:
        """
        Let's be honest: we're lazy!
        We don't want to have to rewrite a vanilla Foreign Key that's already
        been specified elsewhere. Automatically add it to the column list if we
        don't see it there.
        """
        names = [c.name for c in cols]
        for fk in fks:
            for colname in fk.column:
                if colname not in names:
                    cols.append(Col(colname,Int(),False,False,False))
        return cols


    def add_cols(self)->List[str]:
        return ["ALTER TABLE {0} ADD {1}".format(self.name,c.create_col(sqlite=False))
                for c in self.cols if not c.pk]


    def create_table(self
                    ,sqlite  : bool  = False
                    ,if_not  : bool  = False
                    ) -> str:
        """
        Returns the statement necessary to create table, MySQL or SQLite
        """
        cols           = [c.create_col(sqlite) for c in self.cols]
        constraints   = ( [self.pkConstraint()]
                        + self.uniqConstraint()
                        + [str(f) for f in self.fks])

        if_not_str    = 'IF NOT EXISTS' if if_not else ''
        mbConstraints = '' if len(constraints)==0 else '\n\t,'.join(constraints)

        cmd = "CREATE TABLE %s %s\n\t(%s%s)"%(if_not_str
                                             ,self.name
                                             ,'\n\t,'.join(cols)
                                             ,mbConstraints)
        return cmd

    def pkConstraint(self)->str:
        pkCols = [c.name for c in self.cols if c.pk]
        return "\n\t,PRIMARY KEY (%s)"%(','.join(pkCols))

    def uniqConstraint(self)->List[str]:
        ucs = [c.name for c in self.cols if c.uniq]
        if ucs == []:
            return []
        else:
            return ["UNIQUE (%s)"%','.join(ucs)]

    def add_table(self,sqlite_pth:str)->None:
        """
        Adds a table, then its columns
        """
        name = self.name
        cmd  = mkInsCmd('tab',['name','desc'],sqlite=True)
        sqlite_execute(sqlite_pth,cmd,[name,self.desc])
        sqlite_execute(sqlite_pth,namespaceCmd,[name,'Table'])

        tab_id = sqlite_select(sqlite_pth,'SELECT tab_id FROM tab WHERE name=?',[name])[0][0]

        ins_cols = ['col_id','tab_id','name','type','nnull','pk','uniq'
                   ,'auto','ind','virt','dfault']
        for col_id,c in enumerate(self.cols):
            binds    = [col_id,tab_id,c.name,str(c.type),c.nn,c.pk
                       ,c.uniq,c.auto,c.ind,c.virt,str(c.default)]

            cmd = mkInsCmd('col',ins_cols,sqlite=True)
            sqlite_execute(sqlite_pth,cmd,binds)
            sqlite_execute(sqlite_pth,namespaceCmd,['%s.%s'%(name,c.name),'Column'])

    def add_fks(self
               ,sqlite_pth : str
               ,tab_id     : int
               ) -> None:
        """
        Add foreign keys to meta.db (ALL tables need to be added, first)
        """
        for i,fk in enumerate(self.fks):
            insQ = mkInsCmd('fk',['tab_id','fk_id'],sqlite=True)
            sqlite_execute(sqlite_pth,insQ,[tab_id,i])
            fk.add_fk(sqlite_pth,tab_id,i)

    def get_fk(self, t2: 'Table')->'FK':
        for fk in self.fks:
            if fk.table == t2.name:
                return fk
        raise ValueError('Could not find FK between %s and %s'%(self,t2))

    def add_indices(self)->List[Tuple[str,str]]:
        return [("""SELECT COUNT(1) IndexIsThere FROM INFORMATION_SCHEMA.STATISTICS
                    WHERE table_schema=DATABASE() AND table_name='%s' AND index_name='%s';"""%(self.name,c.name)
                ,'ALTER TABLE %s ADD INDEX (%s)'%(self.name,c.name))
                    for c in self.cols if c.ind]


class Col(object):
    """
    typ = SQL datatype {int,str,float}
    nn  = NOT NULL constraint
    pk  = PRIMARY KEY constraint
    uniq = include column in a table-wide UNIQUE constraint
    Notes:
    - SQLite doesn't automatically enforce a NOT NULL constraint on PKs
        ...but we want that.
    """
    def __init__(self
                ,name : str
                ,typ  : SQLType = Int() #str  = 'int'
                ,nn   : bool = False
                ,pk   : bool = False
                ,uniq : bool = False
                ,auto : bool = False
                ,ind  : bool = False
                ,virt : Optional[str] = None
                ,default : Optional[Any] = None
                ) -> None:
        self.name = name
        self.type = typ
        self.nn      = nn or pk
        self.pk      = pk
        self.uniq = uniq
        self.auto = auto
        self.ind  = ind
        self.virt = virt
        self.default = default

    def src(self)->str:
        typ = '' if self.type == 'int' else ",typ='%s'"%self.type
        nn  = '' if self.pk or not self.nn else ',nn=True'
        pk  = '' if not self.pk else ',pk=True'
        uniq= '' if not self.uniq else ',uniq=True'
        auto= '' if not self.auto else ',auto=True'
        ind = '' if not self.ind  else ',ind=True'
        virt = '' if not self.virt else ',virt=%s'%self.virt
        default = '' if self.default is None else ',default=%s'%repr(self.default)
        args = [typ,nn,pk,uniq,auto,ind,virt,default]
        return "Col('%s'%s)"%(self.name,''.join(args))

    def __str__(self)->str:
        return pformat(self.__dict__)

    def __repr__(self)->str:
        return str(self)

    def __eq__(self,other : object)->bool:
        return self.__dict__==other.__dict__

    def create_col(self
                  ,sqlite : bool = False
                  )->str:
        """
        Create statement for column when creating a table.
        NO idea why I need to include 'null' there for the sqlite typechecking...
        """

        dt = str(self.type) # self.typToSQLType(self.type).lower()
        nn = 'NOT NULL' if self.nn else ''
        auto = 'AUTO_INCREMENT' if self.auto else ''
        virt = '' if self.virt is None else "AS (%s)"%self.virt
        dflt = '' if self.default is None else "DEFAULT %s"%(self.default)
        # if sqlite:
        #     if 'var' in dt:
        #         check_dt = 'text' # HACK
        #     else:
        #         check_dt = dt
        #
        #     return "{0} \t{1} {2} {3} CHECK (typeof({0}) in ('{4}','null'))".format(self.name,dt,nn,auto,check_dt)
        # else:
        return "{0} \t{1} {2} {3} {4} {5}".format(self.name,dt,nn,auto,virt,dflt)


class FK(object):
    """
    Representation of a foreign key relationship.
    Use lists for composite foreign keys.

    FOREIGN KEY (job_id) REFERENCES traj (job_id)
    """
    def __init__(self
                ,fkc : Union[List[str],str]
                ,fkt : str
                ,tar : Optional[Union[List[str],str]] = None
                ) -> None:
        self.column  = fkc if isinstance(fkc,list) else [fkc]
        self.table   = fkt
        if tar is None:
            self.target = self.column
        else:
            self.target  = tar if isinstance(tar,list) else [tar]

        assert len(self.column) == len(self.target)

    def __str__(self) -> str:
        col,tab,tar = ','.join(self.column),self.table,','.join(self.target)
        return "FOREIGN KEY (%s) REFERENCES %s (%s)"%(col,tab,tar)

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self,other : object) -> bool:
        return self.__dict__ == other.__dict__


    def add_fk(self
              ,sqlite_pth : str
              ,tab_id     : int
              ,fk_id        : int
              ) -> None:
        """
        Adds FK relation to SQLite meta.db
        """
        for fromC,toC in zip(self.column,self.target):
            from_col = sqlite_select(sqlite_pth,getColCmd,[tab_id,fromC])[0][0]
            try:
                to_tab_id = get_tab_id(sqlite_pth,self.table)
                to_col = sqlite_select(sqlite_pth,getColCmd,[to_tab_id,toC])[0][0]
            except IndexError:
                raise ValueError("Could not find table %s with col %s"%(self.table,toC))

            cmd = mkInsCmd('fk_cols',['tab_id','fk_id','col_id','to_tab','to_col'],sqlite=True)
            sqlite_execute(sqlite_pth,cmd,[tab_id,fk_id,from_col,to_tab_id,to_col])


    def src(self)->str:
        targ = '' if self.target == self.column else ',%s'%self.target
        return "FK({0},'{1}'{2})".format(self.column,self.table,targ)

class View(object):
    def __init__(self,name:str,query:str)->None:
        self.name  = name
        self.query = query

    def src(self)->str:
        return "View('%s','%s')"%(self.name,self.query)
    def __str__(self)->str:
        return pformat(self.__dict__)
    def __repr__(self)->str:
        return str(self)
    def __eq__(self,other : object)->bool:
        return self.__dict__==other.__dict__
    def create_view(self)->str:
        return "CREATE OR REPLACE VIEW %s AS %s"%(self.name,self.query)
    def deps(self)->Tuple[Set[str],Set[str]]:
        return parse_dependencies([self.query])[:2]
    def add_view(self,sqlite_pth:str)->None:
        cmd = mkInsCmd('views',['name','query'],sqlite=True)
        sqlite_execute(sqlite_pth,cmd,[self.name,self.query])
        sqlite_execute(sqlite_pth,namespaceCmd,[self.name,'View'])
