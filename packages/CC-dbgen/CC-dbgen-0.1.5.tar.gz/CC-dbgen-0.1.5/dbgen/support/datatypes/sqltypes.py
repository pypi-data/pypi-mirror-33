# External Modules
from abc import abstractmethod
from re import split
################################################################################

class SQLType(object):
    """
    SQL datatypes
    """
    @abstractmethod
    def __str__(self)->str:
        pass
    def __repr__(self)->str:
        return str(self)
    def __eq__(self,other:object)->bool:
        return self.__dict__==other.__dict__
    @staticmethod
    def from_str(s:str)->'SQLType':
        if 'VARCHAR' in s:
            mem = split(r'\(|\)',s)[1]
            return Varchar(int(mem))
        elif "DECIMAL" in s:
            prec,scale = split(r'\(|\)|,',s)[1:3]
            return Decimal(int(prec),int(scale))
        elif 'INT' in s:
            if   'TINY' in s: kind = 'tiny'
            elif 'BIG'  in s: kind = 'big'
            else:             kind = 'medium'
            signed = 'UNSIGNED' not in s
            return Int(kind,signed)
        elif 'TEXT' in s:
            if   'TINY' in s: kind = 'tiny'
            elif 'MED'  in s: kind = 'medium'
            elif 'LONG' in s: kind = 'long'
            else :            kind = ''
            return Text(kind)
        else:
            raise NotImplementedError("New SQLtype to parse?")
class Varchar(SQLType):
    """
    Varchar
    """
    def __init__(self,mem:int=255)->None:
        self.mem=mem
    def __str__(self)->str:
        return "VARCHAR(%d)"%self.mem

class Decimal(SQLType):
    def __init__(self,prec:int=10,scale:int=3)->None:
        self.prec  = prec
        self.scale = scale
    def __str__(self)->str:
        return "DECIMAL(%d,%d)"%(self.prec,self.scale)

class Int(SQLType):
    def __init__(self,kind:str='medium',signed:bool=True)->None:
        self.kind = kind
        self.signed = signed
    def __str__(self)->str:
        if   self.kind == 'tiny':   core= "TINYINT"
        elif self.kind == 'medium': core= "INTEGER"
        elif self.kind == 'big' :   core= "BIGINT"
        else:
            raise ValueError('unknown Int kind: '+self.kind)
        return core + "" if self.signed else " UNSIGNED"

class Text(SQLType):
    def __init__(self,kind:str='')->None:
        self.kind = kind
    def __str__(self)->str:
        if   self.kind == 'tiny':   return "TINYTEXT"
        elif self.kind == '':       return "TEXT"
        elif self.kind == 'medium': return "MEDIUMTEXT"
        elif self.kind == 'long' :  return "LONGTEXT"
        else:
            raise ValueError('unknown TEXT kind: '+self.kind)

class Date(SQLType):
    def __init__(self)->None:
        pass
    def __str__(self)->str:
        return "DATE"
