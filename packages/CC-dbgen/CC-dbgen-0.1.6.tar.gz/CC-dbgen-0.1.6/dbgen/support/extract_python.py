from typing import Optional,List,Union,Tuple
# External Modules
import os
from os.path import join,exists
from ast import literal_eval
# Internal Modules
from dbgen.support.datatypes.table     import Table,Col,FK,View
from dbgen.support.datatypes.rule import Rule
from dbgen.support.datatypes.func      import Func
from dbgen.support.datatypes.dbg       import  DBG
from dbgen.support.datatypes.misc      import  Arg
from dbgen.support.datatypes.temp      import Temp,TempFunc,Const
from dbgen.support.datatypes.metatemp  import MetaTemp,Block
from dbgen.support.datatypes.sqltypes  import SQLType,Int,Varchar,Text,Decimal
from dbgen.support.utils               import sqlite_select
from dbgen.core.misc                   import maybe
###############################################################################


# Helper function
#----------------
def splt(x:Optional[str],y:Optional[str]=None)->List[Optional[str]]:
    if x is None:
        return [None]*100
    else:
        delim = y if y else ','
        return x.split(delim)  # type: ignore

def extract_dbg(pth:str)->DBG:
    """ Extract everything """
    if exists(pth):
        return DBG(tables = get_tables(pth)
                  ,rules  =  get_rules(pth)
                  ,views  = get_views(pth))
    else:
        raise IOError("No .db file found at "+pth)

def get_views(pth:str)->List[View]:
    q = "SELECT name,QUERY from views"
    qOut = sqlite_select(pth,q)
    return [View(n,q) for n,q in qOut]

def get_tables(pth:str)->List[Table]:
    colQ="""SELECT T.tab_id,T.name,T.desc
                    ,group_concat(C.name,'|')
                    ,group_concat(C.type,'|')
                    ,group_concat(C.nnull,'|')
                    ,group_concat(C.pk,'|')
                    ,group_concat(C.uniq,'|')
                    ,group_concat(C.auto,'|')
                    ,group_concat(C.ind,'|')
                    ,group_concat(COALESCE(C.virt,'None'),'|')
                    ,group_concat(COALESCE(C.dfault,'None'),'|')
            FROM  tab T
            LEFT JOIN col C USING (tab_id)
            GROUP BY T.tab_id
            """
    rawtabs = sqlite_select(pth,colQ)
    table_dict = {}

    for (t_id,tn,td,cn,ct,cnn,cpk,cu,ca,ci,cv,cd) in rawtabs:

        # Add columns
        #-----------
        cols     = []
        spltCols = [cn,ct,cnn,cpk,cu,ca,ci,cv,cd]
        splttr   = lambda x: splt(x,'|')
        for n,t,nn,pk,u,a,i,v,d in zip(*map(splttr,spltCols)):
            typ = SQLType.from_str(t)
            if isinstance(typ,Int):
                d = None if d=='None' else int(d)
            elif isinstance(typ,Decimal):
                d = None if d=='None' else float(d)
            elif isinstance(typ,(Text,Varchar)):
                pass
            else:
                raise NotImplementedError("New type? %s %s"%(str(typ),typ.__class__))

            cols.append(Col(n,typ,nn=='1',pk=='1',u=='1',a=='1',i=='1'
                           ,None if v=="None" else v,None if d=="None" else d))

        # Add FKs
        #--------
        pkQ = """SELECT group_concat(FC.name),TT.name,group_concat(TC.name)
                from fk FK
                join fk_cols FKC USING (tab_id,fk_id)
                join col FC USING  (tab_id,col_id)
                join tab FT USING (tab_id)
                join col TC on FKC.to_tab = TC.tab_id and FKC.to_col = TC.col_id
                join tab TT on FKC.to_tab = TT.tab_id
                where FKC.tab_id = ?
                group by FK.fk_id
                order by FK.fk_id"""
        pkOut = sqlite_select(pth,pkQ,[t_id])
        fks = []
        for fcnames,ttname,tcnames in pkOut:
            fks.append(FK(splt(fcnames),ttname,splt(tcnames))) # type: ignore

        table_dict[tn] = Table(tn,td,cols,fks)

    return list(table_dict.values())

def get_rules(pth:str)->List[Rule]:
    """
    Getting rules...
    """
    #print('\tGetting rules...')

    q = """SELECT rule_id,name,query FROM rule """
    qOut = sqlite_select(pth,q)
    output      = [] # type: List[Rule]
    # For each rule, extract its template, store in tempDict
    for (t_id,name,query) in qOut:
        t = Rule(name     = name
                     ,query     = query
                     ,metatemp  = get_metatemp(pth,t_id)
                     ,template  = get_temp(pth,t_id))
        output.append(t)
    return output

def get_metatemp(pth    : str
                ,t_id   : int
                ) -> MetaTemp:
        """
        Parses a metatemp from meta.db
        """
        # Get Blocks
        #--------------
        #print('\t\tGetting metatemp...')
        blockQ = """SELECT B.name,B.text
                        ,GROUP_CONCAT(BA.name)
                        ,GROUP_CONCAT(COALESCE(BA.ind,'None'))
                        FROM block B
                        LEFT JOIN blockarg BA USING (rule_id,block_id)
                        WHERE B.rule_id = ?
                        GROUP BY B.block_id
                        ORDER BY B.block_id """

        blocksOut = sqlite_select(pth,blockQ,[t_id])
        blocks = [] # type: List[Block]
        for name,txt,names,inds in blocksOut:
            if names is None:
                args = [] # type: List[Arg]
            else:
                args = [Arg(n,None if i=='None' else int(i)) for n,i in zip(*map(splt,[names,inds]))]
            blocks.append(Block(name,txt,args))

        return MetaTemp(blocks)

def get_temp(pth    : str
            ,t_id   : int
            ) -> Temp:
    """
    Parses a template from meta.db
    """
    #print('\t\tGetting temp...')

    # Get TempFuncs
    #--------------
    tfQ = """SELECT F.name,TF.name
                    ,GROUP_CONCAT(TFA.name)
                    ,GROUP_CONCAT(COALESCE(TFA.ind,'None'))
                    FROM tempfunc TF

                    JOIN func F USING (func_id)

                    LEFT JOIN tempfuncarg TFA USING  (rule_id,tempfunc_id)
                    WHERE TF.rule_id = ?
                    GROUP BY TF.tempfunc_id """

    tfOut = sqlite_select(pth,tfQ,[t_id])

    tempfuncs = [] # type: List[TempFunc]
    stdout    = [] # type: ignore

    for (fName,name,tfa_names,tfa_inds) in tfOut:
        if tfa_names == None:
            args = [] # type: List[Arg]
        else:
            args = [Arg(n,None if i=='None' else int(i)) for n,i in zip(*map(splt,[tfa_names,tfa_inds]))]
        tempfuncs.append(TempFunc(fName,name,args))

    # Get Constants
    #--------------

    constQ = """SELECT name,datatype,val
                FROM constants
                WHERE rule_id = ?"""
    constOut = sqlite_select(pth,constQ,[t_id])

    constants = [] # type: List[Tuple[str,Const]]
    for name,dt,val in constOut:
        if 'float' in dt:
            val = float(val)
        elif 'int' in dt:
            val = int(val)
        elif 'dict' in dt:
            val = literal_eval(val)
        elif 'str' in dt:
            pass
        elif 'callable' in dt:
            raise NotImplementedError
        else:
            raise ValueError('bad datatype? '+dt)
        constants.append((name,Const(val)))

    return Temp(tempfuncs=tempfuncs,constants=dict(constants))
