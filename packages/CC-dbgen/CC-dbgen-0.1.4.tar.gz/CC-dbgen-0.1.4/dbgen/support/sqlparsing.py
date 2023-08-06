# External Modules
from typing import  Iterator,Tuple,Set,List,Any,Dict
from sqlparse        import parse             # type: ignore
from sqlparse.sql    import Token             # type: ignore
from sqlparse.tokens import Name,Whitespace   # type: ignore
from abc             import abstractmethod
"""
Functions to assist with the extraction of dependencies from a raw SQL query
"""

class Stmt(object):
    pass

    @abstractmethod
    def parents(self)->Tuple[Set[str],Set[str]]:
        """
        What tables / columns does this statement depend on existing
        """
        raise NotImplementedError

    @abstractmethod
    def children(self)->Tuple[Set[str],Set[str]]:
        """
        What tables (i.e. insertions) / columns does this statement modify?
        """
        raise NotImplementedError

class SelectStmt(Stmt):
    """
    Collection of tokens associated with any SELECT statement
    """
    def __init__(self,tokens:list,alias:dict={})->None:
        eof = [Token(None,'<EOF>')]
        self.tokens = [t for t in tokens if t.ttype != Whitespace] + eof
        self.alias  = alias # type: Dict[str,str]

    def parents(self)->Tuple[Set[str],Set[str]]:
        tabdata,coldata    = set(),set() # type: Tuple[Set[str],Set[Tuple[str,str]]]
        last_tok,penult = '','' # initialize placeholders
        for i,tok in enumerate(self.tokens):
            t = tok.normalized
            if t == '<EOF>': break
            if tok.ttype == Name:
                if self.tokens[i+1].normalized=='.':
                    coldata.add((t,self.tokens[i+2].normalized))
                elif self.tokens[i+1].normalized=='AS':
                    self.alias[self.tokens[i+2].normalized] = t
                    tabdata.add(t)
        cols = set(['%s.%s'%(self.alias.get(t,t),c) for t,c in coldata])
        tabs = tabdata
        return tabs,cols

    def children(self)->Tuple[Set[str],Set[str]]:
        return set(),set()

class InsertStmt(Stmt):
    """
    Any INSERT statment of the form "INSERT INTO <tab> ([cols]) VALUES (...)"
    """
    def __init__(self,tabname:str,inscols:list,insvals:list)->None:
        self.tabname = tabname
        self.inscols = inscols
        self.insvals = insvals
    def parents(self)->Tuple[Set[str],Set[str]]:
        return SelectStmt(self.insvals).parents()
    def children(self)->Tuple[Set[str],Set[str]]:
        cols = ['%s.%s'%(self.tabname,c) for c in self.inscols]
        return set([self.tabname]),set(cols)

class UpdateStmt(Stmt):
    """
    Any UPDATE statment of the form "UPDATE <tab> [AS alias] SET [colval_pairs]"
    """
    def __init__(self,tabname:str,colvals:Iterator,alias:dict)->None:
        self.tabname = tabname
        self.colvals = colvals
        self.alias   = alias
        #print('len colvals  = %d'%len(colvals))
    def parents(self)->Tuple[Set[str],Set[str]]:
        t,c = set(),set()
        for cv in self.colvals:
            i = 4 if self.alias else 2
            pseudoSelect = SelectStmt(cv[i:],self.alias)
            newT,newC = pseudoSelect.parents()
            t.update(newT);c.update(newC)
        return t,c
    def children(self)->Tuple[Set[str],Set[str]]:
        output = set()
        for cv in self.colvals:
            i = 2 if self.alias else 0
            output.add(self.tabname+'.'+cv[i].value)
        #if any(['timestamp' in [x.value for x in cv] for cv in self.colvals]):
        #    import pdb;pdb.set_trace()
        return set(),output

def mkStmt(s:str)->Stmt:
    """
    Convert a Raw SQL string into a Stmt
    """
    #print('PARSING '+s)
    debug = 'UPDATE adsorbate' in s
    #if debug: print('PARSING '+s)
    try:
        toks = parse(s.strip())[0].flatten()
    except IndexError:
        raise ValueError('Could not parse query:\n',s)

    fst = next(toks).normalized
    next(toks)                      # whitespace
    if fst == 'SELECT':
        return SelectStmt(list(toks))

    elif fst == 'INSERT':
        assert next(toks).normalized == 'INTO';next(toks)
        tab = next(toks);next(toks)
        assert next(toks).normalized == '('
        inscols = []
        for t in toks:
            if t.normalized==')': break
            if t.normalized!=',':
                inscols.append(t.value)
        return InsertStmt(tab.value,inscols,list(toks))

    elif fst == 'UPDATE':
        tab = next(toks);next(toks)
        if next(toks).normalized=='AS':
            next(toks)
            alias = {next(toks).normalized:tab}
            next(toks);next(toks)
        else:
            alias = {};next(toks)

        colvals = [[]] # type: list
        l_toks = [t for t in toks if t.ttype !=Whitespace]
        for i,t in enumerate(l_toks):
            if t.normalized == ',' and l_toks[i+1].ttype==Name and l_toks[i+2].value=='=':
                colvals.append([])
            else : colvals[-1].append(t)
        return UpdateStmt(tab.value,list(filter(None,colvals)),alias)
    else:
        raise NotImplementedError

def map_parser(xs : List[str]) -> Tuple[Set[str],Set[str],Set[str],Set[str]]:
    """
    For many SQL statements, create Stmt objects and aggregate dependency info
    """
    pt,pc,ct,cc = set(),set(),set(),set()
    for stmt in map(mkStmt,xs):
        npt,npc = stmt.parents()
        nct,ncc = stmt.children()
        pt.update(npt);pc.update(npc)
        ct.update(nct);cc.update(ncc)
    return pt,pc,ct,cc

################################################################################
# Exported Functions
#-------------------
def parse_dependencies(xs:List[str])->Tuple[Set[str],Set[str],Set[str],Set[str]]:
    """
    List of tables,columns that are queried by the SQL statements
    """
    alltabs,allcols,deptabs,depcols =  map_parser(xs)
    return (alltabs - deptabs,allcols - depcols,deptabs,depcols)
