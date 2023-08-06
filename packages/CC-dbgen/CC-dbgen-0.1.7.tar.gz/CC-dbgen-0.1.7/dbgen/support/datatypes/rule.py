from typing import Optional,List,Dict,Any,Callable

# External Modules
from time            import time
from pprint          import pformat
from tqdm            import tqdm                   # type: ignore
from multiprocessing import Pool,cpu_count
from sqlparse        import format as sql_format   # type: ignore

# Internal Modules
from dbgen.support.sqlparsing         import parse_dependencies
from dbgen.support.datatypes.metatemp import MetaTemp
from dbgen.support.datatypes.temp     import Temp
from dbgen.support.datatypes.func     import Func
from dbgen.support.datatypes.misc     import ExternalError
from dbgen.support.utils              import (sqlexecute,sqlselect,mkInsCmd,sqlite_execute
                                             ,namespaceCmd,func_to_ind,sqlite_select
                                             ,handle_to_ind,ConnectInfo,select_dict)
from dbgen.core.lists   import flatten,concat_map
from dbgen.core.parsing import btw
from dbgen.core.numeric import safe_div
#########################################################################################

class Rule(object):
    """
    Information required to transform the database

    Generally, one must provide:
        - a unique name by which this action can be referred (method_name)
        - the name of the entity/table that is being altered (tab_name)
        - whether or not we're inserting new rows vs updating columns (insert)
        - what prerequiste information is needed beforehand (deps)
        - what information we will be providing (cols)
        - how to get the required information for the rule (query)
        - what operation to transform the inputs (func)
    """

    def __init__(self
                ,name       : str
                ,query      : Optional[str] = None
                ,metatemp   : MetaTemp      = MetaTemp([])
                ,template   : Temp          = Temp([],{})
                ) -> None:

        if query is not None:
            query = sql_format(query, reindent=True).strip()
            query = sql_format(query, reindent=True) # indempotency

        self.name       = name
        self.metatemp   = metatemp
        self.query      = query
        self.template   = template

        # Precompute dependencies of all SQL commands
        mbQuery = [] if self.query is None else [self.query]
        allsql = mbQuery + [b.text for b in self.metatemp.blocks]
        self.deps   = parse_dependencies(allsql)

    def src(self)->str:
        query = '' if self.query is None else '\n\t\t,query="""\n%s"""'%self.query
        temp  = '' if self.template == Temp([],{}) else "\n\t,template=%s"%self.template.src()
        fmtargs = [self.name,query,temp,self.metatemp.src()]
        return "Rule('{0}'{1}{2}\n\t,metatemp={3})".format(*fmtargs)

    def __str__(self)->str:
        return pformat(self.__dict__)

    def __repr__(self)->str:
        return str(self)

    def __eq__(self,other : object)->bool:
        return self.__dict__==other.__dict__


    def dependency_failed(self
                         ,conn : ConnectInfo
                         ) -> Any:
        q = """SELECT child
                FROM META_dependencies
                JOIN META_rule ON parent = method
                WHERE child =%s AND status like '%%failed%%'"""
        output = sqlselect(conn,q,[self.name])
        return True if len(output) == 0 else output

    def run_rule(self
                ,conn    : ConnectInfo
                ,verbose : bool = True
                ,parallel: bool = True
                ) -> None:
        """
        Executes a SQL query, then maps each output over a processing function
        which modifies the database.
        """

        try:
            start = time()

            if self.query is None:
                inputs = [{}] # type: List[dict]
            else:
                inputs = list(select_dict(conn,self.query)) # memory problems if we convert iterator to list?

            q = "UPDATE META_rule SET n_inputs=%s WHERE method=%s"
            sqlexecute(conn,q,[len(inputs),self.name])

            process_raw_args = self.zip_many((self,conn),inputs)
            if parallel:
                cpus = cpu_count()-1 or 1 # play safe, leave one free
                with Pool(cpus + 1 ) as p: # catastrophic failure less likely if we use n-1 available nodes
                    for _ in tqdm(p.imap_unordered(self.process_row,process_raw_args)
                                 ,total=len(inputs)):
                        pass
            else:
                for row in tqdm(process_raw_args):
                    self.process_row(row)

            self.update_status(conn,'completed')
            tot_time = time()-start
            self.update_time(conn,tot_time/60,safe_div(tot_time,len(inputs)))

        except ExternalError as e:
            err = str(e).replace('\\n','\n')
            msg = 'Error when running rule %s\n'%self.name
            print(msg + err)
            self.log_error(conn,msg + err)

    def log_error(self
                 ,conn : ConnectInfo
                 ,err  : str
                 ) -> None:
        self.update_status(conn,'failed')
        q = "UPDATE META_rule SET error=%s WHERE method=%s"
        sqlexecute(conn,q,[err,self.name])

    def update_status(self
                     ,conn : ConnectInfo
                     ,stat : str
                     ) -> None:
        q = "UPDATE META_rule SET status=%s WHERE method=%s"
        sqlexecute(conn,q,[stat,self.name])

    def update_time(self
                   ,conn     : ConnectInfo
                   ,duration : float
                   ,rate     : float
                   ) -> None:
        q = "UPDATE META_rule SET runtime=%s,rate=%s WHERE method=%s"
        sqlexecute(conn,q,[duration,rate,self.name])

    def add_rule(self,sqlite_pth : str) -> None:
        """
        Insert a Rule to the meta.db
        """
        cmd   = mkInsCmd('rule',['name','query'],sqlite=True)
        sqlite_execute(sqlite_pth,cmd,[self.name,self.query])
        sqlite_execute(sqlite_pth,namespaceCmd,[self.name,'Rule'])
        t_id = handle_to_ind(sqlite_pth,self.name)
        self.metatemp.add_metatemp(sqlite_pth,t_id)
        self.template.add_temp(sqlite_pth,t_id)

    @staticmethod
    def zip_many(t:tuple,xs:list)->List[tuple]:
        return [(*t,x) for x in xs]

    @staticmethod
    def process_row(tup : tuple) -> None:
        (t,conn,row) = tup          # unpack
        try:
            t.metatemp.rule_output_processor(conn
                ,t.template.apply_template(row))
        except ExternalError as e:
            def abbreviate(x:Any)->Any:
                if isinstance(x,str) and len(x) > 1000:
                    return x[:1000]+'...'
                else:
                    return x
            row_ = {k:abbreviate(v) for k,v in row.items()}
            raise ExternalError('%s failed with inputs %s \n%s'%(t.name,row_,e))
