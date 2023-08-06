from typing import List,Dict,Any,Optional,Tuple
# External Modules
from pprint import pprint,pformat
from decimal import Decimal

# Internal Modules
from dbgen.support.utils import sqlexecute,sqlselect,sqlexecutemany,mkInsCmd,sqlite_execute,ConnectInfo,addQs
from dbgen.support.datatypes.table import Table,FK
from dbgen.support.datatypes.misc import Arg,noIndex
################################################################################
################################################################################
class MetaTemp(object):
    """
    blocks   - define how the ruleed Query inputs are fed back into the DB
    """
    def __init__(self,blocks : List['Block']) -> None:
        self.blocks   = blocks

    def src(self)->str:
        return 'MetaTemp([%s])'%('\n\t,'.join(b.src() for b in self.blocks))

    def __str__(self)->str:
        return pformat(self.__dict__)

    def __repr__(self)->str:
        return str(self)

    def __eq__(self,other : object)->bool:
        return self.__dict__==other.__dict__



    def rule_output_processor(self
                                  ,conn        : ConnectInfo
                                  ,result_dict : Dict[str,Any]
                                  ,verbose        : bool = False
                                  ) -> None:
        """
        Processes the output of a rule's query
        """

        for block in self.blocks:
            result_dict[block.name] = block.func(conn,result_dict,verbose)

    def add_metatemp(self
                    ,sqlite_pth   : str
                    ,rule_id : int
                    ) -> None:
        """
        Add to sqlite meta.db
        """
        for bId,block in enumerate(self.blocks):
            block.add_block(sqlite_pth,rule_id,bId)


class Block(object):
    """
    Execute a SQL statement after processing the Template.
        Inputs either refer to Template outputs ('stdout') or to other Blocks
        (by name, which should be unique)
        Possibly return something if statement is select.
    """
    def __init__(self
                ,name    : str
                ,text      : str
                ,args       : List[Arg] = []
                ) -> None:

        self.name    = name
        self.text    = text.strip()
        self.args    = args


    def src(self)->str:
        fmtargs = [self.name
                  ,'"""\n%s"""'%self.text
                  ,'\n\t\t\t,'.join(a.src() for a in self.args)]
        return "Block('{0}'\n\t\t,text={1}\n\t\t,args=[{2}])".format(*fmtargs)
    def __str__(self)->str:
        return pformat(self.__dict__)

    def __repr__(self)->str:
        return str(self)

    def __eq__(self,other : object)->bool:
        return self.__dict__==other.__dict__

    def func(self
            ,conn        : ConnectInfo
            ,curr_dict : dict
            ,verbose   : bool = True
            ) -> Optional[List[tuple]]:
        """
        Creates a function which takes in a namespace dictionary and executes its
        block script (possibly using the namespace for inputs). Its result will
        get added to the namespace.
        """
        args = [arg.arg_get(curr_dict) for arg in self.args]
        maxlen = 1
        for a in args:
            assert isinstance(a,(int,str,float,list,bytes,Decimal,type(None))), "Arg (%s) BAD DATATYPE %s IN NAMESPACE "%(a,a.__class__)
            if isinstance(a,list):
                if maxlen != 1: # variable has been set
                    try:
                        assert(len(a) in [1,maxlen]), 'Can\'t broadcast: maxlen = %d, len a = %d (%s)'%(maxlen,len(a),str(a)) # preconditions for broadcasting
                    except:
                        import pdb;pdb.set_trace()
                else:
                    maxlen = len(a)

        def process_arg(x:Any)->list:
            if isinstance(x,list) and len(x)!=maxlen:
                return maxlen*x # broadcast
            elif not isinstance(x,list):
                return  maxlen * [x]
            else:
                return x

        # now all args should be lists of the same length
        broadcasted = [process_arg(x) for x in args]

        binds = list(zip(*broadcasted))

        if self.text[:6].lower()=='select':
            # we're probably selecting to get a PK, take the first result no matter what
            def app(x:tuple)->List[tuple]:
                    return sqlselect(conn,self.text,x)[0] # type: ignore

            def mbBox(x:tuple)->Any:
                if len(x)==1: return x[0]
                else: return x
            uniqbinds = list(set(binds))
            try:
                output = {b:mbBox(app(b)) for b in uniqbinds} # type: ignore
            except IndexError:
                    print('failed to find a result after query failed:\n'+self.text)
                    print('binds are : '+pformat(list(zip(self.args,uniqbinds[0]))))
                    import pdb;pdb.set_trace()
                    return []

            return [output.get(x) for x in binds] # type: ignore
        else:
            if len(self.args)==0:
                sqlexecute(conn,self.text)
            else:
                sqlexecutemany(conn,self.text,binds)
            return None

    def add_block(self
                 ,sqlite_pth : str
                 ,trans_id   : int
                 ,block_id   : int
                 ) -> None:
        """
        """
        block_icmd = mkInsCmd('block',['rule_id','block_id','text','name'],sqlite=True)
        sqlite_execute(sqlite_pth,block_icmd,[trans_id,block_id,self.text,self.name])
        for i,a in enumerate(self.args):
            a.add_arg(sqlite_pth,'meta',trans_id,block_id,i)

    @staticmethod
    def maybe_index(d   : dict
                   ,arg : Tuple[str,Optional[int]]
                   ) -> Any:
        """
        This is exact copy from (some version of) temp.py
        """
        if arg[1] is None:
            return d[arg[0]]
        else:
            return d[arg[0]][arg[1]]

################################################################################
################################################################################
# MetaTemp Shortcuts
#-------------------
def PureSQL(strs : List[str])->MetaTemp:
    """ Executes a series of SQL statements in order """
    return MetaTemp([Block(str(i),s) for i,s in enumerate(strs)])

def SimpleInsert(tab   : str
                ,cols  : List[str]
                ) -> MetaTemp:
    """
    Assume that the insert columns have corresponding variables in the namespace
    """
    args   = noIndex(cols)
    qmarks = ','.join(['%s']*len(cols))
    return MetaTemp([Block('insert'
                          ,"""INSERT INTO {0} ({1})
                                  VALUES ({2})
                                  ON DUPLICATE KEY
                                UPDATE {3} = {3}""".format(tab
                                                          ,','.join(cols)
                                                          ,qmarks
                                                          ,cols[0])
                          ,args)])

def SimpleUpdate(tab  : Table
                ,cols : List[str]
                ) -> MetaTemp:
    """
    Assume that the insert columns AND primary keys have corresponding variables
    in the namespace
    """
    pk_cols = [c.name for c in tab.cols if c.pk == True]
    args    = noIndex(cols+pk_cols)
    set     = addQs(cols,',')
    where   = addQs(pk_cols,' AND ')

    return MetaTemp([Block('update'
                          ,'UPDATE %s SET %s WHERE %s'%(tab.name,set,where)
                           ,args)])

def SimpleUpsert(ins_tab   : Table
                ,ins_cols  : List[str]
                ,fk_tab    : Table
                ) -> MetaTemp:
    """
    Let's say we compute an entity (A) associated with another entity (B).
    - We want to insert the A instance into the A table (if it doesn't exist).
    - We want to record the PK of this A instance an store it as a FK in B table.

    ins_tab   - 'A' table described above
    cols       - properties with which to insert an A instance
    fk_tab    - name of the 'B' table described above

    We assume that:
        - there exists exactly one foreign key from B to A
        - we are going to populate all columns of foreign key if it's composite
        - whatever was inserted will uniquely identify an A object (e.g. 'raw'
            for structure, possibly not necessarily the PKs of A)
        - variables from template associated with various columns are equal to
          their column names

    WARNING THIS WILL BE A PROBLEM IF THERE'S A NAMESPACE COLLISION IN KEY NAMES

    SAFER WOULD BE TO MAKE THE 'key' FOR COLUMNS TO BE '<table>.<column>'
    """

    insert_args   = noIndex(ins_cols)
    insert_qmarks = ','.join(['%s']*len(ins_cols))
    fmt_args0     = [ins_tab.name,','.join(ins_cols),insert_qmarks,ins_cols[0]]
    insert_block  = Block('insert'
                         ,"""INSERT INTO {0} ({1})
                             VALUES ({2}) ON DUPLICATE KEY
                            UPDATE {3}={3}""".format(*fmt_args0)
                         ,insert_args)

    ins_pks = [c.name for c in ins_tab.cols if c.pk]
    where  = addQs(ins_cols,' AND ')
    fmt_args1 = [','.join(ins_pks),ins_tab.name,where]
    get_id_block = Block('get_id'
                        ,'SELECT {0} FROM {1} WHERE {2}'.format(*fmt_args1)
                        ,insert_args)

    fk              = fk_tab.get_fk(ins_tab)
    fk_pks          = [c.name for c in fk_tab.cols if c.pk]
    setvals      = addQs(fk.column,' , ')
    whereagain   = addQs(fk_pks,' AND ')
    args          = [Arg('get_id',i) for i in range(len(fk.column))]
    fmt_args2    = [fk_tab.name,setvals,whereagain]
    args.extend(noIndex(fk_pks))

    update_block = Block('update'
                        ,'UPDATE {0} SET {1} WHERE {2}'.format(*fmt_args2)
                        ,args)

    return MetaTemp([insert_block, get_id_block, update_block])
