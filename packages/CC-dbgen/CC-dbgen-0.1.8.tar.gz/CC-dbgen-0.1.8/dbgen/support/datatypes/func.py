# External Modules
from typing                import Any,Type,TupleMeta,CallableMeta # type: ignore
from typing                import Union as U,Callable as Call,TypeVar as TV
from json                  import JSONEncoder,dumps
from pprint                import pformat
from ast                   import parse,Lambda,walk
from os                    import linesep
from sys                   import version_info
from importlib.util        import spec_from_file_location,module_from_spec
from inspect               import (getdoc,signature,isfunction,getsourcefile # type: ignore
                                  ,getmembers,getsourcelines,_empty)

from pymatgen              import Structure  # type: ignore
import ase  # type: ignore
from networkx.classes.multigraph import MultiGraph # type: ignore

# Iternal Modules
from dbgen.support.utils import sqlite_execute,mkInsCmd,namespaceCmd
from dbgen.support.datatypes.datatypes import (DataType,Tuple,List,Dict,AnyType
                                              ,Base,NoneType,TypeVar,Union
                                              ,Callable)


################################################################################
# MOVE THIS TO UTILS IF WE END UP NEEDING TO SERIALIZE ANYTHING ELSEWHERE
#-----------------------------------------------------------------------
class Enc(JSONEncoder):
    """
    Use arbitrary serialization methods, if they're provided. Currently, this
        is used to serialize Python datatypes in a way that can be parsed into
        dbgenHaskell's "DataType" (via Aeson.fromJSON).
    """
    def default(self, o : Any)->dict:
        if hasattr(o,'toJSON'):
            return o.toJSON()
        else:
            return JSONEncoder.default(self,o)
################################################################################
version   = version_info[1]
assert version > 5, "Stop using old python3 (need 3.x, x > 5)"
class Func(object):
    """
    A function that can be used during the DB generation process.
    It is specified by:
        - a 'handle' (which is referred to in the "template" field
            of Rule objects)
        - a (full) path to a file that contains ONLY that function (at the top level)
    """
    def __init__(self,func : Call) -> None:

        # Determine if a path was given or a function
        # We'll slowly deprecate the use of paths
        #-----------------------------------------
        assert callable(func), 'Need to initialize function with a callable'

        # Extract basic info from function object
        #----------------------------------------
        self.func = func
        self.name = func.__name__           # type: ignore
        self.doc  = getdoc(func)
        self.src  = self.get_source(func)  # type: ignore
        sig       = signature(func)         # type: ignore
        self.nIn  = len(sig.parameters)

        # Determine # of outputs
        #----------------------
        output    = sig.return_annotation
        if str(output)[:11]=='typing.List':
            self.nOut = len(output.__args__)
        elif isinstance(output,TupleMeta): # type: ignore
            self.nOut = len(output.__args__)
        else:
            self.nOut = 1

        # Determine types
        #-----------------
        self.iT = [self.get_datatype(x.annotation) for x in sig.parameters.values()]
        self.oT = self.get_datatype(sig.return_annotation)

    def __eq__(self,other : object)->bool:
        return self.__dict__==other.__dict__

    def __str__(self)->str:
        return pformat(self.__dict__)

    def __repr__(self)->str:
        return str(self)

    def __hash__(self)->int:
        return hash(self.name)

    def apply(self,*args : Any)->Any:
        return self.func(*args) # type: ignore

    def add_func(self
                ,sqlite_pth : str
                ) -> None:
        """
        Performs analysis of PYTHON functions
        """


        cols = ['name','source','docstring'
               ,'inTypes_json','outType_json','inTypes','outType','n_in','n_out']

        binds= [self.name,self.src,self.doc
               ,dumps(self.iT,indent=4,cls=Enc)
               ,dumps(self.oT,indent=4,cls=Enc)
               ,str(self.iT),str(self.oT),self.nIn,self.nOut]
        try:
            sqlite_execute(sqlite_pth,mkInsCmd('func',cols,sqlite=True),binds)
        except Exception as e:
            raise ValueError('error with func "%s": '%self.name + str(e))
        sqlite_execute(sqlite_pth,namespaceCmd,[self.name,'Func'])


    @staticmethod
    def path_to_func(pth:str) -> Callable:
        """
        Assumes we have files with one sole function in them
        """
        spec = spec_from_file_location('',pth)
        if spec.loader is None:
            raise ValueError(pth)
        else:
            mod  = module_from_spec(spec)
            spec.loader.exec_module(mod)

            def check(o:Callable)->bool:
                return isfunction(o) and getsourcefile(o)==pth

            funcs = [o for o in getmembers(mod) if check(o[1])]

            assert len(funcs)==1,"Bad input file %s has %d functions, not 1"%(pth,len(funcs))

            return funcs[0][1]

    @staticmethod
    def get_source(f:Callable)->str:
        """Return the source code, even if it's lambda function.
        Source: http://xion.io/post/code/python-get-lambda-code.html
        """
        try:
            source_lines, _ = getsourcelines(f)
        except (IOError, TypeError):
            raise ValueError

        # Skip `def`-ed functions and long lambdas
        if len(source_lines) > 1:
            return linesep.join(source_lines).strip()

        source_text = linesep.join(source_lines).strip()

        # Find the AST node of a lambda definition so we can locate it in the source code
        source_ast = parse(source_text)
        lambda_node = next((node for node in walk(source_ast)
                            if isinstance(node, Lambda)), None)

        if lambda_node is None:  # could be a single line `def fn(x): ...`
            raise ValueError

        # HACK: Source will have some trailing junk after their definition.
        # Unfortunately, AST nodes only keep their _starting_ offsets from the original source, so we have to determine the end ourselves. We do that by gradually shaving extra junk from after the definition.
        lambda_text = source_text[lambda_node.col_offset:]
        lambda_body_text = source_text[lambda_node.body.col_offset:]
        min_length = len('lambda:_')  # shortest possible lambda expression
        while len(lambda_text) > min_length:
            try:
                # What's annoying is that sometimes the junk even parses,
                # but results in a *different* lambda. You'd probably have to  be deliberately malicious to exploit it but here's one way:
                # >bloop = lambda x: False, lambda x: True
                # >get_short_lamda_source(bloop[0])
                # Ideally, we'd just keep shaving until we get the same code, but that most likely won't happen because we can't replicate the exact closure environment.
                code = compile(lambda_body_text, '<unused filename>', 'eval')
                # Thus the next best thing is to assume some divergence due to e.g. LOAD_GLOBAL in original code being LOAD_FAST in
                # the one compiled above, or vice versa. But the resulting code should at least be the same *length*
                # if otherwise the same operations are performed in it.
                if len(code.co_code) == len(getattr(f,'__code__').co_code):
                    return lambda_text
            except SyntaxError:
                pass
            lambda_text      = lambda_text[:-1]
            lambda_body_text = lambda_body_text[:-1]

        raise ValueError

    @staticmethod
    def get_datatype(t:Type)->DataType:
        """
        Convert a Python Type object into a simpler ADT
        """
        strt = str(t)
        if   t == float:            return Base("Float")
        elif t == int:              return Base("Int")
        elif t == str:              return Base("Str")
        elif t == bool:             return Base("Bool")
        elif t == type(None):       return NoneType()

        elif t in [ase.atoms.Atoms,ase.Atoms,'Atoms']:
            return Base("Atoms")
        elif t in [Structure,'Structure']:
            return Base("Atoms")
        elif strt in ['BULK',"<class 'bulk_enumerator.bulk.BULK'>"]:
            return Base("BULK")
        elif t == MultiGraph:
            return Base("MultiGraph")

        elif str(t.__class__)==str(Union) or strt[:12]=='typing.Union':
            if version > 5:
                return Union([Func.get_datatype(x) for x in t.__args__])
            else:
                return Union([Func.get_datatype(x) for x in t.__union_set_params__])

        elif isinstance(t,TupleMeta): # type: ignore
            if version > 5:
                return Tuple([Func.get_datatype(x) for x in t.__args__])
            else:
                return Tuple([Func.get_datatype(x) for x in t.__tuple_params__])

        elif isinstance(t,CallableMeta): # type: ignore
            from_args = [Func.get_datatype(x) for x in t.__args__[:-1]]
            to_arg    = Func.get_datatype(t.__args__[-1])
            return Callable(from_args,to_arg)

        elif isinstance(t,TV): # type: ignore
            return TypeVar(t.__name__)

        elif strt[:11]=='typing.List':
            return List(Func.get_datatype(t.__args__[0]))

        elif strt[:11]=='typing.Dict':
            a1,a2 = [Func.get_datatype(x) for x in t.__args__]
            return Dict(a1,a2)

        elif strt == 'typing.Any' or t == _empty: # type: ignore
            return AnyType()

        else:
            print('NEW DATATYPE FOUND')
            import pdb;pdb.set_trace()
            raise NotImplementedError()

    @staticmethod # NEED TO LOAD FROM META.DB
    def dict2DT(x : dict)->DataType:
        tag = x.get('tag')
        if tag == 'Base':
            return Base(x['contents'])
        elif tag == 'Tuple':
            return Tuple([Func.dict2DT(y) for y in x['contents']])
        else:
            raise NotImplementedError('new case for dict2DT: ',x)

###############
# Spceial Funcs
#--------------
identity = Func(lambda x: x)
