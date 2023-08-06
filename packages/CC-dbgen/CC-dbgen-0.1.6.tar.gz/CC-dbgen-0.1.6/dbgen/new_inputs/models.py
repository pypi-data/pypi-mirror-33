# Internal modules
from dbgen.support.datatypes.model      import Model
from dbgen.support.datatypes.func       import Func
from dbgen.new_inputs.objects           import uni
from dbgen.new_inputs.relations         import relations

###############################################################################
if __name__=='__main__':
    from dbgen.main import parser
    args = parser.parse_args()
    m = Model(uni,relations)
    m.run(reset = args.reset,catalog=args.catalog)
