
#Typing imports
import typing as typ

#External imports
from os             import environ
from argparse       import ArgumentParser
from pprint         import pformat
from distutils.util import strtobool
from ast            import literal_eval
from json           import load

# Internal Modules
from dbgen.support.utils          import ConnectInfo
from dbgen.core.misc              import levenshteinDistance
from dbgen.inputs.development     import dbg
"""
Command line interface for executing a database update

Requires DB_JSON environment variable to specify database that will be modified

The following flags control program behavior:
    - verbose
    - local
    - reset
    - add
    - meta
    - only
    - xclude
    - jobs
    - catalog
    - test
    - parallel

"""
#Internal Imports
import parser # type: ignore

class CLICommand:
    short_description = "Command line interface for executing a database update"
    description = ("""
The following flags control program behavior:
        - verbose
        - local
        - reset
        - add
        - meta
        - only
        - xclude
        - jobs
        - catalog
        - test
        - parallel""")

    @staticmethod
    def add_arguments(parser : 'parser') -> None: # type: ignore
        parser.add_argument('--verbose'
                           ,default = False
                           ,type    = lambda x:bool(strtobool(x))
                           ,help    = """Leave it off please - hard to find a reasonable
                                        amount of things that's neither too little nor
                                        too much ... maybe the input for this should
                                        actually be 'high 'low' or 'medium'?""")

        parser.add_argument('--local'
                           ,default = False
                           ,type    = lambda x:bool(strtobool(x))
                           ,help    = 'Default: if on sherlock, don\'t run local')

        parser.add_argument('--reset'
                           ,default = False
                           ,type    = lambda x:bool(strtobool(x))
                           ,help    = 'Nuke the DB first - needed if you make schema changes')

        parser.add_argument('--add'
                           ,default = False
                           ,type    = lambda x:bool(strtobool(x))
                           ,help    = 'Try to add columns (if you make benign schema additions)')

        parser.add_argument('--meta'
                           ,default = False
                           ,type    = lambda x:bool(strtobool(x))
                           ,help    = 'Make a meta.db')

        parser.add_argument('--only'
                           ,default = ''
                           ,help    = 'Run only the (space separated) rules')

        parser.add_argument('--xclude'
                           ,default = 'underlying ads_triple'
                           ,help    = 'Do not run the (space separated) rules')

        parser.add_argument('--jobs'
                           ,default = False
                           ,type    = lambda x:bool(strtobool(x))
                           ,help    = 'Run all job_loading rules (takes time to rerun even if no new jobs)')

        parser.add_argument('--catalog'
                           ,default = False
                           ,type    = lambda x:bool(strtobool(x))
                           ,help    = 'Run only the catalog job loading rule ')

        parser.add_argument('--test'
                           ,default = ''
                           ,nargs   = 2
                           ,help    = 'Give a Tranform Name and an input dictionary (as parsable string) to test')

        parser.add_argument('--parallel'
                           ,default = True
                           ,type    = lambda x:bool(strtobool(x))
                           ,help    = 'Parallelize processing of multiple Query inputs. (Turn off if using pdb)')

    @staticmethod
    def run(args : typ.Any) -> None:
        """
        Executes DB modifying procedure described by a DBG instance
        """
        print('args are: \n'+pformat(args))


        if args.test:
            # Don't interact with database
            #------------------------------------
            dic = literal_eval(args.test[1])
            assert isinstance(dic,dict), "We need a dictionary to test a Rule's input"
            dbg.test_input(args.test[0],dic)
        else:
            # Actually interact with database
            #------------------------------------
            if args.local:
                db = ConnectInfo()
            else:
                with open(environ['DB_JSON'],'r') as f:
                    db = ConnectInfo(**load(f))

            if args.meta:
                dbg.test_meta() # create a meta-db

            # Determine which job-loading rules to include
            #------------------------------------------------------------
            if not args.jobs:
                args.xclude+=''' stray_gpaw_logfiles
                                 stray_qe_logfiles
                                 stray_chargemol_logfiles ''' # these T's ONLY run if --jobs

            if (not args.reset) and (not (args.catalog or args.jobs)):
                args.xclude+=''' catalog ''' # this run if EITHER --jobs OR --catalog...provided we didn't just nuke DB

            # Process string inputs
            #------------------------
            only   = set(args.only.split())
            xclude = set(args.xclude.split()) - only

            # Verify every  rule excluded/included by name actually exists
            # if first 5 chars match or within edit distance of 5, suggest alternatives
            #------------------------------------------------------------------------------------
            for w in (only | xclude):
                match = False
                close = []
                for n in [t.name for t in dbg.rules]:
                    d = levenshteinDistance(w,n)
                    upW,upN = max(len(w),5), max(len(n),5) # variables for safe indexing
                    if d == 0:
                        match = True
                        break
                    elif d < 5 or w[:upW] == n[:upN]:
                        close.append(n) # keep track of near-misses
                if not match:
                    did_you = "Did you mean %s"%close if close else ''
                    raise ValueError("No match found for %s\n%s"%(w,did_you))

            dbg.run_all(db
                       ,only    = only
                       ,xclude  = xclude
                       ,reset   = args.reset
                       ,add     = args.add
                       ,verbose = args.verbose
                       ,parallel= args.parallel)
