import typing

class DataType(object):
    def toJSON(self)->dict: raise NotImplementedError()

class AnyType(DataType):
    def toJSON(self)->dict:
        return {'tag':'AnyType'}

    def __str__(self)->str:
        return 'Any'

    def __repr__(self)->str:
        return self.__str__()

class NoneType(DataType):
    def toJSON(self)->dict:
        return {'tag':'NoneType'}

    def __str__(self)->str:
        return 'None'

    def __repr__(self)->str: return self.__str__()

class Base(DataType):
    def __init__(self,unBase:str)->None:
        self.unBase = unBase

    def toJSON(self)->dict:
        return {'tag':'Base','unBase':self.unBase}

    def __str__(self)->str:
        return '"%s"'%self.unBase

    def __repr__(self)->str: return self.__str__()

class TypeVar(DataType):
    def __init__(self,name:str)->None:
        self.name = name

    def toJSON(self)->dict:
        return {'tag':'TypeVar','name':self.name}

    def __str__(self)->str:
        return '"%s"'%self.name


class Callable(DataType):
    def __init__(self
                ,args:typing.List[DataType]
                ,out:DataType
                )->None:
        self.c_args= args
        self.out = out

    def toJSON(self)->dict:
        return {'tag':'Callable'
                ,'cArgs':[x.toJSON() for x in self.c_args]
               ,'out':self.out.toJSON()
               }

    def __str__(self)->str:
        ar = ' -> '
        return ar.join(map(str,self.c_args))+ar+str(self.out)

    def __repr__(self)->str:
        return self.__str__()

class Union(DataType):
    def __init__(self,args:typing.List[DataType])->None:
        self.args=args

    def toJSON(self)->dict:
        return {'tag':'Union'
               ,'uArgs':[x.toJSON() for x in self.args]}

    def __str__(self)->str:
        return '{%s}'%(','.join(sorted(map(str,self.args))))

    def __repr__(self)->str:
        return self.__str__()

class Tuple(DataType):
    def __init__(self,args:typing.List[DataType])->None:
        self.args= args
    def toJSON(self)->dict:
        return {'tag':'Tuple'
               ,'tArgs':[x.toJSON() for x in self.args]}


    def __str__(self)->str:
        return '(%s)'%(','.join(map(str,self.args)))

    def __repr__(self)->str: return self.__str__()

class List(DataType):
    def __init__(self,content:DataType)->None:
        self.content=content

    def toJSON(self)->dict:
        return {'tag':'List'
               ,'unList':self.content.toJSON()}

    def __str__(self)->str:
        return '[%s]'%(str(self.content))

    def __repr__(self)->str:
        return self.__str__()

class Dict(DataType):
    def __init__(self,fromT:DataType,toT:DataType)->None:
        self.key = fromT
        self.val = toT

    def toJSON(self)->dict:
        return {'tag':'Dict'
                ,'key': self.key.toJSON()
                ,'val': self.val.toJSON()}

    def __str__(self)->str:
        return '{ %s : %s }'%(str(self.key),str(self.val))

    def __repr__(self)->str: return self.__str__()
