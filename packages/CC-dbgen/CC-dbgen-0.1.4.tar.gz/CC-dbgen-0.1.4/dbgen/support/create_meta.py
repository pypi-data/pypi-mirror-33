
# External Modules
import os
# Internal Modules
from dbgen.support.utils              import sqlite_execute,mkInsCmd
from dbgen.support.datatypes.table	import Table,Col,FK
from dbgen.support.datatypes.sqltypes	import Varchar

"""
Define the schema for a SQLite meta.db, which can be used to represent the
entire DbGen process.
"""

################################################################################
tables = [Table('tab'
            ,cols=[Col('tab_id',        pk = True)
                  ,Col('name',Varchar(),nn = True)
                  ,Col('desc',Varchar(),nn = True)])
    ,Table('views'
            ,cols=[Col('view_id',           pk = True)
                  ,Col('name',  Varchar(),  nn = True)
                  ,Col('query', Varchar(),  nn = True)])
    ,Table('col'
        ,cols=[Col('tab_id',        pk = True)
              ,Col('col_id',        pk = True)
              ,Col('name',Varchar(),nn = True)
              ,Col('type',Varchar(),nn = True)
              ,Col('nnull',         nn = True)
              ,Col('pk',            nn = True)
              ,Col('uniq',          nn = True)
              ,Col('auto',          nn = True)
              ,Col('ind',           nn = True)
              ,Col('virt',  Varchar())
              ,Col('dfault',Varchar())
              ]
        ,fks=[FK('tab_id','tab')])

    ,Table('fk'
        ,cols=[Col('tab_id', pk = True)
              ,Col('fk_id',  pk = True)]
        ,fks=[FK('tab_id','tab')])

    ,Table('fk_cols'
        ,cols=[Col('tab_id',  pk = True)
              ,Col('fk_id',   pk = True)
              ,Col('col_id',  pk = True)
              ,Col('to_tab',  nn = True)
              ,Col('to_col',  nn = True)]
        ,fks=[FK(['tab_id','fk_id'],'fk')
             ,FK(['tab_id','col_id'],'col')
             ,FK(['to_tab','to_col'],'col',['tab_id','col_id'])])

    ,Table('func'
        ,cols=[Col('func_id',               pk = True)
              ,Col('name',        Varchar(),nn = True)
              ,Col('pth',         Varchar(),nn = True)
              ,Col('source',      Varchar(),nn = True)
              ,Col('docstring',   Varchar(),nn = True)
              ,Col('language',    Varchar(),nn = True)
              ,Col('inTypes_json',Varchar(),nn = True)
              ,Col('outType_json',Varchar(),nn = True)
              ,Col('inTypes',     Varchar(),nn = True)
              ,Col('outType',     Varchar(),nn = True)
              ,Col('n_in',                  nn = True)
              ,Col('n_out',                 nn = True)])

    ,Table('rule'
        ,cols=[Col('rule_id',      pk=True)
              ,Col('name',   Varchar(), nn=True)
              ,Col('query',  Varchar())])

    ,Table('tempfunc'
        ,cols=[Col('rule_id',              pk = True)
              ,Col('tempfunc_id',               pk = True)
              ,Col('func_id',                   nn = True)
              ,Col('name',          Varchar(),  nn = True)]
        ,fks = [FK('rule_id','rule')
               ,FK('func_id','func')])

    ,Table('tempfuncarg'
        ,cols=[Col('rule_id',              pk = True)
              ,Col('tempfunc_id',               pk = True)
              ,Col('tempfuncarg_id',            pk = True)
              ,Col('name',          Varchar(),  nn = True)
              ,Col('ind')]
        ,fks=[FK(['rule_id','tempfunc_id'],'tempfunc')])

    ,Table('constants'
        ,cols=[Col('rule_id',          pk = True)
              ,Col('const_id',              pk = True)
              ,Col('name',      Varchar(),  nn = True)
              ,Col('datatype',  Varchar(),  nn = True)
              ,Col('val',       Varchar(),  nn = True)]
        ,fks = [FK('rule_id','rule')])

    ,Table('libfuncs'
        ,cols=[Col('rule_id',              pk = True)
              ,Col('const_id',                  pk = True)
              ,Col('name',          Varchar(),  nn = True)
              ,Col('func_id',                   nn = True)]
        ,fks = [FK('func_id','func')
               ,FK(['rule_id'],'rule')])

    ,Table('blockarg'
        ,cols=[Col('rule_id',              pk = True)
              ,Col('block_id',                  pk = True)
              ,Col('blockarg_id',               pk = True)
              ,Col('name',          Varchar(),  nn = True)
              ,Col('ind')]
        ,fks=[FK(['rule_id','block_id'] ,'block')])

    ,Table('block'
        ,cols = [Col('rule_id',            pk = True)
                ,Col('block_id',                pk = True)
                ,Col('text',        Varchar(),  nn = True)
                ,Col('name',        Varchar(),  nn = True)]
        ,fks = [FK('rule_id','rule')])

    ,Table('namespace'
        ,cols=[Col('namespace_id',              pk = True)
              ,Col('name',          Varchar(),  nn = True,uniq = True)
              ,Col('type',          Varchar(),  nn = True,uniq = True)])

    ,Table('config'
        ,cols=[Col('config_id',             pk = True)
              ,Col('verbose',               nn = True)
              ,Col('retry',                 nn = True)
              ,Col('simulate',              nn = True)
              ,Col('run_only',  Varchar())
              ,Col('run_except',Varchar())]
        ,fks=[FK('connection_id','connection')])

    ,Table('connection'
        ,cols=[Col('connection_id' ,        pk = True)
              ,Col('name',      Varchar())
              ,Col('hostname',  Varchar(),  nn = True,uniq = True)
              ,Col('user',      Varchar(),  nn = True,uniq = True)
              ,Col('port',                  nn = True,uniq = True)
              ,Col('database',  Varchar(),  nn = True,uniq = True)
              ,Col('password',  Varchar(),  nn = True,uniq = True)])
        ]

###############################################################################
# Main
#-----
def create_empty(pth   : str
                ,local : bool = False
                ) -> None:
    """
    Creates a brand new database file containing no data (except default config)
    """
    if os.path.exists(pth):
        print('removing db at ',pth)
        os.remove(pth)

    # Create all tables
    #----------------
    for t in tables:
        sqlite_execute(pth,t.create_table(sqlite=True))

    # Populate two possible MySQL connections: localhost vs SUNCAT
    #-----------------------------------------------------------------
    insertConn = mkInsCmd('connection',['name','hostname','port'
                                       ,'user','password','database']
                        ,sqlite=True)
    user = os.environ['USER']
    sqlite_execute(pth,insertConn,['localhost',"127.0.0.1",3306,user,user, "suncat"])

    # Initialize Config
    #----------------
    config = 1 if local else 2
    init_config = mkInsCmd('config'
                          ,['verbose','retry','simulate','connection_id']
                          ,sqlite = True)

    sqlite_execute(pth,init_config,[1,1,0,config])


if __name__=='__main__':
    create_empty('temp.db')
