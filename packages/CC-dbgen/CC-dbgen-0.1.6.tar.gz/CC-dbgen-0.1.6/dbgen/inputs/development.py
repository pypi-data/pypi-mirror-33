
# Internal Modules

from dbgen.inputs.basics      import (tables as basic_tables
                                     ,rules as basic_rules
                                     ,views as basic_views)

from dbgen.inputs.adsorbates  import (tables as ads_tables
                                     ,rules  as ads_rules
                                     ,views  as ads_views)

from dbgen.inputs.experiment  import (tables     as expt_tables
                                           ,rules as expt_rules)

from dbgen.inputs.extra       import (tables     as x_tables
                                           ,rules as x_rules)

from dbgen.inputs.graphs      import (tables     as grph_tables
                                           ,rules as grph_rules)

from dbgen.inputs.learning    import (tables     as ml_tables
                                           ,rules as ml_rules)

from dbgen.inputs.references  import (tables     as ref_tables
                                           ,rules as ref_rules)

from dbgen.inputs.rxn         import (tables     as rxn_tables
                                           ,rules as rxn_rules)

from dbgen.inputs.species     import (tables     as sp_tables
                                           ,rules as sp_rules)

from dbgen.inputs.catalog     import (rules  as cat_rules)


from dbgen.support.datatypes.dbg import DBG
################################################################################

tables = (ads_tables + basic_tables + expt_tables + x_tables   + grph_tables
        + ml_tables  + grph_tables  + ml_tables   + ref_tables + rxn_tables
        + sp_tables)

rules = (ads_rules  + basic_rules + expt_rules + x_rules
            + grph_rules + ml_rules    + grph_rules + ml_rules
            + ref_rules  + rxn_rules   + sp_rules   + cat_rules)

views = basic_views + ads_views


dbg = DBG(tables = tables
         ,rules  = rules
         ,views  = views)
