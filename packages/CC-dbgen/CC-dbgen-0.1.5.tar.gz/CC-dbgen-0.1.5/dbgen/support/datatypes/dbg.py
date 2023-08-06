from typing import List,Set,Tuple,Dict,Callable,Any

# External Modules
from copy   import deepcopy
from pprint import pformat,pprint
import networkx as nx                  # type: ignore
from MySQLdb import OperationalError # type: ignore

# Internal Modules
from dbgen.support.datatypes.table     import Table,Col,View
from dbgen.support.datatypes.func      import Func
from dbgen.support.datatypes.rule      import Rule
from dbgen.support.datatypes.misc      import onlyTest,xTest,fTest
from dbgen.support.datatypes.sqltypes  import Varchar,Decimal,Text

from dbgen.support.utils               import (sqlexecute,sqlselect,ConnectInfo
                                                  ,mkInsCmd ,get_tab_id,topsort_with_dict)
from dbgen.support.create_meta         import create_empty
from dbgen.core.lists                  import flatten
#########################################################################################

class DBG(object):
    """
    Container for the three necessary components to define a database update
    """
    def __init__(self
                #,funcs      : List[Func]
                ,tables     : List[Table]
                ,rules      : List[Rule]
                ,views      : List[View]  = []
                ) -> None:
        # Functions
        #self.funcs     = funcs

        # Schema
        self.views      = views
        self.tables     = self.order_tables(tables)

        self.fkdict = {} # type: Dict[str,Tuple[str,str]]
        for t in self.tables:
            for fk in t.fks:
                for c1,c2 in zip(fk.column,fk.target):
                    if '%s.%s'%(t.name,c1) not in self.fkdict: #HACK - how to handle when a column is part of multiple FKs?
                        self.fkdict['%s.%s'%(t.name,c1)] = (fk.table,'%s.%s'%(fk.table,c2))

        # Rules
        self.rules = rules # unordered
        self.rules = self.order_rules(rules)

    def __str__(self)->str:
        return pformat(self.__dict__)

    def __repr__(self)->str:
        return str(self)

    def __eq__(self,other : object)->bool:
        return self.__dict__==other.__dict__

    def str_to_tab(self,tabname:str)->Table:
        for t in self.tables:
            if t.name == tabname: return t
        raise ValueError('cannot find table '+tabname)

    def view_deps(self
                 ,tablist:Set[str]
                 ,collist:Set[str]
                 ) -> Tuple[Set[str],Set[str]]:
        """
        REMOVE views from the parsed tables that are dependencies.  These views
        depend on tables and columns themselves, so return
        """
        dep_dict =  {v.name:v.deps() for v in self.views}

        tabs,cols   = set(),set() # type: Set[str],Set[str]

        for tab in tablist:
            if tab in dep_dict.keys():
                ts,cs = dep_dict[tab]
                tabs.update(ts)
                cols.update(cs)
            else:
                tabs.add(tab)

        return tabs,cols | collist

    def derive_deps(self,t : Rule)->List[str]:
        """
        For a given rule, first determine everything it depends on (parent tabs)
        Then iterate through every other rule and determine what it affects (child tabs)
        If there is any intersection, then this rule depends on that one

        This has to be done here (rather than at the Rule level) because
        there is dependency on dbg.views and dbg.tables (FKs)
        """
        debugFrom = 'cell_info'
        debugTo   = None # 'populate_struct_traj_atom_cell'

        output, n = [],t.name

        raw_parent_tabs,raw_parent_cols,child_tabs,child_cols = t.deps
        viewed_p_tabs,viewed_p_cols   = self.view_deps(raw_parent_tabs,raw_parent_cols) # correct for effect of Views
        viewed_c_tabs,viewed_c_cols = self.view_deps(child_tabs,child_cols)           # correct for effect of Views

        fk_tabs,fk_cols = self.get_fk_deps(child_cols)

        produced_tab_pks = set(flatten([['%s.%s'%(tab,c.name)
                                 for c in self.str_to_tab(tab).cols if c.pk]
                                    for tab in viewed_c_tabs]))

        # Finally, determine all tables/cols that this Rule depends on
        parent_tabs =  (viewed_p_tabs | fk_tabs) - child_tabs
        parent_cols = ((viewed_p_cols | fk_cols) - viewed_c_cols) - produced_tab_pks

        for other in self.rules:
            o = other.name
            if o != n:
                _,_,other_child_tabs,other_child_cols = other.deps
                disjoint = ( other_child_tabs.isdisjoint(parent_tabs)
                           & other_child_cols.isdisjoint(parent_cols))
                if debugFrom==n and debugTo==o:
                    print("DEBUGGING DEPENDENCIES\n#######################\n")
                    if t.query:
                        print("%s's query \n"%n+pformat(t.query))
                    else:
                        print("%s's metatemp "%n)
                        for b in t.metatemp.blocks: print(b.text)
                    print("%s's metatemp "%o)
                    for b in other.metatemp.blocks: print(b.text)
                    print('\nRESULTS\n########\n')
                    print("%s's parent_tabs \n\t"%n   + pformat(parent_tabs))
                    print("%s's parent_cols \n\t"%n   + pformat(parent_cols))
                    print("%s's child_tabs\n\t"%o + pformat(other_child_tabs))
                    print("%s's child_cols\n\t"%o + pformat(other_child_cols))
                    import pdb;pdb.set_trace()
                if not disjoint:
                    output.append(other.name)

        return output

    def get_fk_deps(self
                   ,colstrs : Set[str]
                   ) -> Tuple[Set[str],Set[str]]:
        """
        If we insert into TAB.COL and that is a FK to TAB2.COL2, then we have
        another dependency we need to account for
        """
        fktab,fkcol = set(),set()
        deps = map(self.fkdict.get,colstrs)
        for d in deps:
            if d is not None:
                fktab.add(d[0])
                fkcol.add(d[1])
        return (fktab,fkcol)

    @staticmethod
    def order_tables(tabs : List[Table])->List[Table]:
        """
        Order the tables, so that they can be created (in MySQL) without
        violating FK constraints
        """
        G = nx.DiGraph()
        G.add_nodes_from([t.name for t in tabs])
        tab_dict = {t.name:t for t in tabs}
        for t in tabs:
            for f in t.fks:
                G.add_edge(f.table,t.name)
        return topsort_with_dict(G,tab_dict)

    def order_rules(self,ts : List[Rule]) -> List[Rule]:
        """
        Sort rules such that dependencies in queries are respected.
        """
        G = nx.DiGraph()
        G.add_nodes_from([t.name for t in ts])
        t_dict = {t.name:t for t in ts}
        for t1 in ts:
            deps = self.derive_deps(t1)
            for t2 in ts:
                if t2.name in deps:
                    G.add_edge(t2.name,t1.name)
        return topsort_with_dict(G,t_dict)


    def make_metatables(self,conn : ConnectInfo)->None:
        """
        Initialize metatables
        """
        metatables = [Table('META_rule'
                        ,cols = [Col('id',pk=True,auto=True)
                                ,Col('method',Varchar(),nn=True)
                                ,Col('status',Varchar(),nn=True)
                                ,Col('runtime',Decimal())
                                ,Col('n_inputs')
                                ,Col('rate',Decimal())
                                ,Col('error',Text())])
                      ,Table('META_dependencies'
                          ,cols = [Col('id',pk=True,auto=True)
                                ,Col('parent',Varchar(),nn=True)
                                ,Col('child',Varchar(),nn=True)])]

        for ta in metatables:
            sqlexecute(conn,'DROP TABLE IF EXISTS '+ta.name)
            sqlexecute(conn,ta.create_table())

        q  = mkInsCmd('META_rule',['method','status'],sqlite=False)
        dq = mkInsCmd('META_dependencies',['child','parent'],sqlite=False)
        for tr in self.rules:
            sqlexecute(conn,q,[tr.name,'initialized'])
            for dep in self.derive_deps(tr):
                sqlexecute(conn,dq,[tr.name,dep])

    def run_all(self
               ,conn    : ConnectInfo
               ,only    : Set[str]  = set()
               ,xclude  : Set[str]  = set()
               ,reset   : bool = False
               ,add     : bool = False
               ,verbose : bool = True
               ,parallel: bool = True
               ) -> None:
        """
        Execute all rules
        """
        print('starting dbgen...')

        self.make_metatables(conn)

        if reset:
            for ta in reversed(self.tables):
                try:
                    sqlexecute(conn,'DROP TABLE IF EXISTS '+ta.name)
                except:
                    raise ValueError("""\t\t\tIn mysql workbench do the following:
                                set session foreign_key_checks = 0 ;
                                <DROP ALL TABLES USING THE SIDEBAR>
                                set session foreign_key_checks = 1 ;""")
        elif add:
            print('trying to add new columns...')
            for ta in self.tables:
                for sqlexpr in ta.add_cols():
                    try:
                        sqlexecute(conn,sqlexpr)
                    except OperationalError:
                        pass
            print('\tdone trying to add new columns.')

        for ta in self.tables:
            sqlexecute(conn,ta.create_table(if_not=True))
            for chk,stmt in ta.add_indices(): #get a SQL error when I try this...
                if not sqlselect(conn,chk):
                    sqlexecute(conn,stmt)

        for v in self.views:
            sqlexecute(conn,v.create_view())

        for rule in self.rules:
            testdict = {onlyTest : [only]
                       ,xTest    : [xclude]
                       ,fTest    : [conn]}
            run = True # flag for passing all tests
            for test,args in testdict.items():
                test_output = test.run_test(rule,*args) # type: ignore
                if test_output is not True:
                    print('\tNot running rule ',rule.name)
                    rule.update_status(conn,test_output)
                    run = False
                    break
            if run:
                print('\tRunning rule ',rule.name)
                rule.update_status(conn,'running')
                rule.run_rule(conn
                           ,verbose
                           ,parallel)

    def create_dbg(self,sqlite_pth:str)->None:
        """
        Creates a whole database using a Python DBG instance
        """
        create_empty(sqlite_pth,local=False)
        for t in self.tables:
            t.add_table(sqlite_pth)
        for t in self.tables:
            tab_id = get_tab_id(sqlite_pth,t.name)
            t.add_fks(sqlite_pth,tab_id)
        #for func in self.funcs:
        #    func.add_func(sqlite_pth)
        for tr in self.rules:
            tr.add_rule(sqlite_pth)
        for v in self.views:
            v.add_view(sqlite_pth)

    def test_input(self
                  ,tr_name : str
                  ,inp     : dict
                  ) -> None:
        t = [tr for tr in self.rules if tr.name == tr_name][0]
        print(t.template.apply_template(inp))

    def test_meta(self)->None:
        """
        Create meta.db and confirm that conversion process is reversible
        """
        from dbgen.support.extract_python import extract_dbg

        self.create_dbg('meta.db')
        dbg_ = extract_dbg('meta.db')
        if self!=dbg_:
            self.diff(dbg_) # print out differences, if any
        assert self == dbg_, 'Something wrong with input or DBG <-> meta.db'

    def diff(self,dbg:'DBG')->None:
        """
        If one expects to DBG's to be equal and they aren't, diff them.
        """
        attrs = ['funcs','tables','views','rules']
        fNames,tNames,vNames,trNames = [[[x.name for x in getattr(d,attr)] for d in [self,dbg]] for attr in attrs]
        # if len(self.funcs)!=len(dbg.funcs):
        #     print("Different number of funcs: \n{} \n{} ".format(*fNames))
        #     return None
        # else:
        #     for f,f2 in zip(self.funcs,dbg.funcs):
        #         assert f.name==f2.name, "Different function orderings {}\n{}".format(*fNames)
        #         if f!=f2:
        #             print('Functions differ for %s\n%s\n%s'%(f.name,pformat(f),pformat(f2)))
        #             return None
        if len(self.tables)!=len(dbg.tables):
            print("Different number of tables: \n{}\n{}".format(*tNames))
            return None
        else:
            for t,t2 in zip(self.tables,dbg.tables):
                assert t.name==t2.name, "Different table ordering {} vs \n {}".format(*tNames)
                if t!=t2:
                    print('Tables differ for '+t.name)
                    if t.name!=t2.name:
                        print('\tNames differ \n\t %s \n%s '%(t.name,t2.name))
                    elif t.desc!=t2.desc:
                        print('\tDescriptions differ\n\t %s \n%s '%(t.desc,t2.desc))
                    for c,c2 in zip(t.cols,t2.cols):
                        if c!=c2:
                            print('\tColumns differ \n\t %s \n%s '%(c,c2))
                    for fk,fk2 in zip(t.fks,t2.fks):
                        if fk!=fk2:
                            print('\FKs differ \n\t %s \n%s '%(fk,fk2))
                    return None
        if len(self.views)!=len(dbg.views):
            print("Different number of views: \n{}\n{}".format(*vNames))
            return None
        else:
            for v,v2 in zip(self.views,dbg.views):
                assert v.name==v2.name, "Different ordering of views  \n{}\n{}".format(*vNames)
                if v!=v2:
                    print("Views differ for %s \n%s \n%s"%(v.name,pformat(v),pformat(v2)))
        if len(self.rules)!=len(dbg.rules):
            print("Different number of rules: {}\n{} ".format(*trNames))
            return None
        else:
            for tr,tr2 in zip(self.rules,dbg.rules):
                assert tr.name==tr2.name, "ordering different {} \n {}".format(*trNames)
                if tr!=tr2:
                    print('Rules differ for %s \n%s\%s'%(tr.name,pformat(tr),pformat(tr2)))
                    return None
        print("Tables don't differ")
