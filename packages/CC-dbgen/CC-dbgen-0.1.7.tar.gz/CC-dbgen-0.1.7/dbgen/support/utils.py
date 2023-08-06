# External Modules
from typing     import List
from sqlite3    import connect as connect_lite
from pprint     import pformat,pprint
from time       import sleep
from sql        import Table,Join                   # type: ignore
from MySQLdb    import Warning,OperationalError     # type: ignore
from networkx   import Graph,NetworkXUnfeasible     # type: ignore
from networkx.algorithms import lexicographical_topological_sort,simple_cycles # type: ignore

from warnings import filterwarnings
filterwarnings("ignore", category = Warning)

# Internal Modules
from dbgen.support.datatypes.misc import ConnectInfo

"""
Tools for creating a database containing instructions for DBGen
"""

##############################################################################
# Interface with DB
#------------------
def sqlite_execute(db_path    : str
                  ,sqlcommand : str
                  ,binds      : list = []
                  ) -> None:
    """
    Execute a SQL statement that modifies the database
    """
    assert sqlcommand.lower()[:6] != 'select'
    #print(sqlcommand)
    with connect_lite(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('PRAGMA foreign_keys = ON')
        cursor.execute(sqlcommand, binds)
        output_array = cursor.fetchall()
        conn.commit()

def sqlite_select(db_path    : str
                 ,sqlcommand : str
                 ,binds      : list = []
                 ,mk_dict    : bool = False
                 ) -> list :
    """
    Select and return a list of tuples
    """
    def dict_factory(cursor, row):  # type: ignore
        return {col[0] : row[idx] for idx, col in enumerate(cursor.description)}

    assert sqlcommand.lower()[:6] == 'select'

    with connect_lite(db_path) as conn:
        cursor = conn.cursor()

        if mk_dict:
            cursor.row_factory = dict_factory

        cursor.execute(sqlcommand, binds)
        output_array = cursor.fetchall()
    return output_array

# Shortcuts
###########

def mkInsCmd(tabName : str
            ,names   : List[str]
            ,sqlite  : bool = False
            ) -> str:
    delim = ['?'] if sqlite else ['%s']
    dup    = ' ' if sqlite else ' ON DUPLICATE KEY UPDATE {0}={0}'.format(names[0])
    ins_names = names if sqlite else ['%s.%s'%(tabName,n) for n in names]
    return "INSERT INTO %s (%s) VALUES (%s) %s"%(tabName
                                             ,','.join(ins_names)
                                             ,','.join(delim*len(names))
                                             ,dup)
def mkUpdateCmd(tabName  : str
                ,names   : List[str]
                ,keys    : List[str]
                ) -> str:
    return "UPDATE %s SET %s WHERE %s"%(tabName
                                             ,addQs(names,',')
                                             ,addQs(keys,' AND '))

namespaceCmd = mkInsCmd('namespace',['name','type'],sqlite=True)

def handle_to_ind(pth:str,name:str)->int:
    cmd = 'SELECT rule_id FROM rule WHERE name = ?'
    try:
        return sqlite_select(pth,cmd,[name])[0][0]
    except IndexError:
        raise ValueError('Could not find rule '+name)

def func_to_ind(pth:str,name:str)->int:
    cmd = 'SELECT func_id FROM func WHERE name = ?'
    try:
        return sqlite_select(pth,cmd,[name])[0][0]
    except IndexError:
        raise ValueError('Could not find function '+name)

def get_tab_id(pth:str,name:str)->int:
    cmd = 'SELECT tab_id FROM tab WHERE name = ?'
    try:
        return sqlite_select(pth,cmd,[name])[0][0]
    except IndexError:
        raise ValueError('Could not find table '+name)
##############################################################################

def select_dict(conn  : ConnectInfo
               ,q     : str
               ,binds : list = []
               ) -> List[dict]:
    print('SELECTING with: ',q)
    with conn.mk_conn(mk_dict=True) as cxn: # type: ignore
        if 'group_concat' in q.lower():
            cxn.execute("SET SESSION group_concat_max_len = 1000000")
        cxn.execute(q,args=binds)
        return cxn.fetchall()

def sqlselect(conn  : ConnectInfo
             ,q     : str
             ,binds : list = []
             ) -> List[tuple]:
    #print('\n\nSQLSELECT ',q)#,binds)
    with conn.mk_conn() as cxn: # type: ignore
        if 'group_concat' in q.lower():
            cxn.execute("SET SESSION group_concat_max_len = 100000")
        cxn.execute(q,args=binds)
        return cxn.fetchall()

def sqlexecute(conn  : ConnectInfo
              ,q     : str
              ,binds : list = []
              ) -> None:
    #print('\n\nSQLEXECUTE ',q)#,binds)
    with conn.mk_conn() as cxn: # type: ignore
        cxn.execute("SET SESSION auto_increment_offset = 1")
        cxn.execute("SET SESSION auto_increment_increment = 1")
        while True:
            try:
                cxn.execute(q,args=binds)
                break
            except OperationalError as e:
                if  e.args[0] not in [1205,1213]: # deadlock error codes
                    sleep(10)
                    raise OperationalError(e)

def sqlexecutemany(conn  : ConnectInfo
                  ,q     : str
                  ,binds : List[list]
                  ) -> None:
    #print('executemany Q: ', q,binds)
    with conn.mk_conn() as cxn: # type: ignore
        cxn.execute("SET SESSION auto_increment_offset = 1")
        cxn.execute("SET SESSION auto_increment_increment = 1")

        while True:
            try:
                cxn.executemany(q,args=binds)
                break
            except OperationalError as e:
                if  e.args[0] not in [1205,1213]: # deadlock error codes
                    sleep(10)
                    raise OperationalError(e)
# ##############################################################################
# String shortcuts
#----------------
def addQs(xs:list,delim:str)->str:
    """ Ex: ['a','b','c'] + ',' ==> 'a = %s, b = %s, c = %s' """
    return delim.join(['{0} = %s'.format(x) for x in xs])

def topsort_with_dict(G:Graph,d:dict)->List:
    try:
        sortd = list(lexicographical_topological_sort(G))
        return [d[x] for x in sortd]
    except NetworkXUnfeasible:
        pprint(list(simple_cycles(G)))
        raise ValueError("(Cycle found)")
