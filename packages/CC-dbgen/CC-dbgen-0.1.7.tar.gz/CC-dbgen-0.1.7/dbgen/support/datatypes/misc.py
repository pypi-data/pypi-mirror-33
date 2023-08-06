# External Modules
from typing import Optional,Any,List,Callable,TYPE_CHECKING
if TYPE_CHECKING:
    from dbgen.support.datatypes.rule import Rule

from MySQLdb import connect,Connection,OperationalError             # type: ignore
from MySQLdb.cursors import Cursor,DictCursor                       # type: ignore
from time import sleep
from os import environ
from random import random
from pprint import pformat
################################################################################

class ExternalError(Exception):
    """
    Custom class for catching errors that occur in code external to dbgen
    """
    def __init__(self, message : str) -> None:
        super().__init__(message)

################################################################################
localuser = environ["USER"]

class ConnectInfo(object):
    """MySQL connection info """
    def __init__(self
                ,host   : str = '127.0.0.1'
                ,port   : int = 3306
                ,user   : str = localuser
                ,passwd : str = localuser
                ,db     : str = 'suncat'
                ) -> None:
        self.host   = host
        self.port   = port
        self.user   = user
        self.passwd = passwd
        self.db     = db

    def __str__(self)->str:
        return pformat(self.__dict__)

    def __eq__(self,other : object)->bool:
        return self.__dict__==other.__dict__

    def mk_conn(self
               ,mk_dict : bool = False
               ,attempt : int  = 10
               ) -> Connection:
        try:
            con = connect(host   = self.host
                          ,port   = self.port
                          ,user   = self.user
                          ,passwd = self.passwd
                          ,db     = self.db
                          ,cursorclass = DictCursor if mk_dict else Cursor
                          ,connect_timeout=28800)
                          #,wait_timeout = 28800
                          #,interactive_timeout = 28800)

        except OperationalError as e:
            if attempt > 0:
                sleep(5)
                con = self.mk_conn(mk_dict,attempt-1)
            else:
                raise OperationalError(e)
        con.query('SET SESSION wait_timeout=28800')
        return con
################################################################################
class Arg(object):
    """
    How a function refers to a namespace
    """

    def __init__(self
                ,name : str
                ,ind  : Optional[int] = None
                ) -> None:
        self.name = name
        self.ind = ind

    def src(self)->str:
        ind = '' if self.ind is None else ',%s'%self.ind
        return "Arg('%s'%s)"%(self.name,ind)
    def arg_get(self,dic:dict)->Any:
        try:
            val = dic[self.name]
            if self.ind is None:
                return val
            else:
                try:
                    return val[self.ind]
                except IndexError:
                    args= [self.name,self.ind,val,pformat(dic)]
                    msg = 'cannot find {0}''s index {1} in {2} \ndic = {3}'
                    raise IndexError(msg.format(*args))
                except TypeError:
                    raise TypeError('cannot index into %s: '%val.__class__,val)
        except KeyError:
            raise KeyError('could not find %s in '%self.name,list(dic.keys()))

    def __str__(self)->str:
        suffix = '' if self.ind is None else '[%d]'%self.ind
        return 'Arg(%s%s)'%(self.name,suffix)

    def __repr__(self)->str:
        return str(self)

    def __eq__(self,other : object)->bool:
        return self.__dict__==other.__dict__

    def add_arg(self
               ,sqlite_pth : str
               ,arg_kind   : str
               ,trans_id   : int
               ,next_id    : int
               ,arg_id     : int
               ) -> None:
        from dbgen.support.utils import mkInsCmd,sqlite_execute
        if arg_kind == 'meta':
            tab = 'blockarg'
        elif arg_kind == 'temp':
            tab = 'tempfuncarg'
        else:
            raise NotImplementedError

        id_col = '%s_id'%(tab[:-3]) # blockarg -> block_id
        q = mkInsCmd(tab,['rule_id',id_col,tab+'_id','name','ind'],sqlite=True)
        sqlite_execute(sqlite_pth,q,[trans_id,next_id,arg_id,self.name,self.ind])

def noIndex(xs:List[str])->List[Arg]:
    """
    At some point we represented arguments as a dictionary with namespace
    elements as keys and an optional index as values. Frequently we don't want
    to index, so this function simplifies writing the values.
    """
    return [Arg(x,None) for x in xs]

###############

class Test(object):
    """
    Execute a test before running rule. If it returns True, the test is
    passed, otherwise it returns an object which is fed into the "message"
    function. This prints a message: "Not Executed (<string of object>)"
    """
    def __init__(self
                ,test    : Callable[['Rule',Any],Any]
                ,message : Callable[[Any],str]
                ) -> None:
        self.test = test
        self.message = message

    def run_test(self,t:'Rule',*args:Any)->Any:
        output = self.test(t,*args)
        if output is True:
            return True
        else:
            return self.message(output)



onlyTest = Test(lambda t,o: (len(o) == 0) or (t.name in o) # type: ignore
               ,lambda x: "Rule not in 'Only' input specification")
xTest = Test(lambda t,x:  t.name not in x # type: ignore
            ,lambda x: "Rule in 'Exclude' input specification")
fTest = Test(lambda t,conn: t.dependency_failed(conn)
            ,lambda x: "Rule depends on failed jobs %s"%pformat(x))
