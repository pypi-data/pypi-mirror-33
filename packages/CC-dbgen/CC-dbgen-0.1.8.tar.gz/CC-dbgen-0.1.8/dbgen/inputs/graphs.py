# External
import os
# Internal
from dbgen.support.datatypes.table     import Table,Col,FK
from dbgen.support.datatypes.table     import Table,Col,FK,View
from dbgen.support.datatypes.temp      import Temp,TempFunc,SimpleTemp
from dbgen.support.datatypes.misc      import Arg,noIndex
from dbgen.support.datatypes.metatemp  import SimpleUpsert,SimpleUpdate,SimpleInsert,PureSQL,MetaTemp,Block
from dbgen.support.datatypes.rule      import Rule
from dbgen.support.datatypes.sqltypes  import Text,Decimal
from dbgen.support.utils               import addQs,mkInsCmd
from dbgen.core.lists                  import flatten

##########################################################################################
##########################################################################################
##########################################################################################
# CONSTANTS
###########
pypth = os.path.dirname(__file__)

cell_args = [Arg('cell',i) for i in range(9)]
cell_cols = ['a0','a1','a2','b0','b1','b2','c0','c1','c2']
from dbgen.scripts.IO.parse_chargemol        import parse_chargemol
from dbgen.scripts.IO.anytraj                import anytraj
from dbgen.scripts.Pure.Atoms.traj_to_json   import traj_to_json
from dbgen.scripts.Pure.Atoms.json_to_traj   import json_to_traj
from dbgen.scripts.Pure.Atoms.get_cell       import get_cell
from dbgen.scripts.Pure.Atoms.get_atom       import get_atom
from dbgen.scripts.Pure.Graph.mk_graph       import mk_graph
from dbgen.scripts.Pure.Graph.graph_to_json  import graph_to_json
from dbgen.scripts.Pure.Misc.identity        import identity
##########################################################################################


bond = Table('bond'
    ,desc="A bond between two atoms identified by chargemol"
    ,cols = [Col('job_id',              pk = True)
            ,Col('struct_id',           pk = True)
            ,Col('atom1',               pk = True)
            ,Col('atom2',               pk = True)
            ,Col('bond_id',             pk = True)
            ,Col('bondorder',Decimal(), nn = True)
            ,Col('distance', Decimal(), nn = True)
            ,Col('pbc_x',               nn = True)
            ,Col('pbc_y',               nn = True)
            ,Col('pbc_z',               nn = True)
            ,Col('h_bond')]
    ,fks  = [FK('job_id',             'chargemol_job',  'job_id')
            ,FK(['struct_id','atom1'],'atom',           ['struct_id','atom_id'])
            ,FK(['struct_id','atom2'],'atom',           ['struct_id','atom_id'])])

chargemol_atom = Table('chargemol_atom'
    ,desc = "Properties of an atom + a chargemol job (e.g. DDEC charge)"
    ,cols = [Col('job_id',                  pk = True)
            ,Col('struct_id',               pk = True)
            ,Col('atom_id',                 pk = True)
            ,Col('charge',      Decimal(),  nn = True)]
    ,fks  = [FK('job_id',               'chargemol_job')
            ,FK(['struct_id','atom_id'],'atom')])

graph_params = Table('graph_params'
    ,desc = "Settings needed to create a graph out of a chargemol job"
    ,cols = [Col('graph_params_id',       pk = True,auto = True)
            ,Col('include_frac',Decimal(),nn = True,uniq = True)
            ,Col('group_cut',   Decimal(),nn = True,uniq = True)
            ,Col('min_bo',      Decimal(),nn = True,uniq = True)])


graph = Table('graph'
    ,desc = """Properties of graphs produced by chargemol analysis
            (combination of chargemol job + graph parameters)"""
    ,cols = [Col('job_id',            pk = True)
            ,Col('graph_params_id',   pk = True)
            ,Col('raw',Text(),        nn = True)
            ,Col('num_nodes')
            ,Col('num_edges')
            ,Col('num_hbonds')]
    ,fks  = [FK('job_id','chargemol_job')
            ,FK('graph_params_id','graph_params')])
#############################################################################
chargemol_map = Table('chargemol_map'
    ,desc = 'Mapping table to relate a job to plausible chargemol_jobs'
    ,cols = [Col('job_id',   pk = True)
            ,Col('charge_id',pk = True)]
    ,fks   = [FK('job_id',      'alljob')
             ,FK('charge_id','chargemol_job','job_id')])

chargemol_job = Table('chargemol_job'
        ,desc = 'Jobs that compute bond order analysis with Chargemol'
        ,cols = [Col('job_id',   pk=True)
                ,Col('calc_id')
                ,Col('struct_id')
                ,Col('bonddata',Text('long'))]
        ,fks  = [FK('job_id',   'alljob')
                ,FK('calc_id',  'calc')
                ,FK('struct_id','struct')])

tables = [bond,chargemol_atom,graph_params,graph,chargemol_map,chargemol_job]
##########################################################################################
##########################################################################################
##########################################################################################

get_chargemol_struct = Rule(name='get_chargemol_struct'
    ,query = """SELECT chargemol_job.job_id,J.stordir,J.anytraj
                FROM chargemol_job  JOIN alljob as J USING (job_id)
                WHERE chargemol_job.struct_id is null
                AND NOT J.deleted"""
    ,template = Temp(tempfuncs = [TempFunc(traj_to_json
                                           ,name='raw'
                                          ,args=[Arg('anytraj')])
                                  ,TempFunc(get_cell
                                                ,name = 'cell'
                                             ,args = [Arg('raw')])
                                 ,TempFunc(get_atom
                                           ,args = [Arg('raw')])]) # returns ([ax]m,[ay]m,...)

    ,metatemp = MetaTemp([Block(name = 'insert_cell'
                               ,text = mkInsCmd('cell',cell_cols,sqlite=False)
                               ,args = cell_args)

                         ,Block(name='query_cell'
                                ,text=('SELECT C.cell_id FROM cell AS C WHERE '
                                      +addQs(['C.%s'%x for x in cell_cols],' AND '))
                                ,args=cell_args)

                                 ,Block(name  = 'insert_struct'
                                        ,text = """INSERT INTO struct (raw,rawhash,cell_id)
                                                   VALUES (%s,SHA2(%s,512),%s)
                                                ON DUPLICATE KEY UPDATE cell_id=cell_id"""
                                       ,args = [Arg('raw'),Arg('raw'),Arg('query_cell',0)])

                         ,Block(name='query_struct'
                                 ,text='SELECT S.struct_id FROM struct AS S WHERE S.rawhash = SHA2(%s,512)'
                                ,args=[Arg('raw')])

                         ,Block(name = 'insert_atom'
                                ,text = mkInsCmd('atom',['struct_id','atom_id','element_id'
                                                      ,'x','y','z','constrained','magmom','tag']
                                                ,sqlite=False)
                               ,args= [Arg('query_struct')]
                                        +[Arg('get_atom',i) for i in range(1,9)])


                        ,Block(name='insert'
                             ,text="UPDATE chargemol_job SET struct_id=%s WHERE job_id=%s"
                             ,args=[Arg('query_struct'),Arg('job_id')])]))

parse_chgml_output = ['atom1','atom2','bond_id','pbc_x','pbc_y','pbc_z'
                     ,'distance','bondorder','atom_id','charge']

bond_cols = ['job_id','struct_id','atom1','atom2','bond_id'
            ,'pbc_x','pbc_y','pbc_z','distance','bondorder']

chgmol_atom_cols = ['job_id','struct_id','atom_id','charge']

unpackargs = [TempFunc(identity
                      ,name = x
                      ,args = [Arg('parse_chargemol',i)])
              for i,x in enumerate(parse_chgml_output)]

populate_bond = Rule('populate_bond'
    ,query = """SELECT C.job_id,S.struct_id,J.stordir
                FROM chargemol_job AS C
                    JOIN alljob        AS J USING (job_id)
                    JOIN struct AS S USING (struct_id)
                WHERE (C.job_id,S.struct_id) NOT IN (SELECT B.job_id,B.struct_id FROM bond AS B)
                AND NOT J.deleted"""
    ,template   = Temp(tempfuncs = unpackargs
                                 + [TempFunc(parse_chargemol
                                            ,args=noIndex(['stordir','anytraj']))
                                   ,TempFunc(anytraj
                                               ,args=[Arg('stordir')])] )
    ,metatemp   = MetaTemp([Block(name = 'insert_bond'
                                 ,text = mkInsCmd('bond',bond_cols,sqlite=False)
                                 ,args = noIndex(bond_cols))
                            ,Block(name   = 'insert_atom'
                                    ,text = mkInsCmd('chargemol_atom',chgmol_atom_cols,sqlite=False)
                                    ,args = noIndex(chgmol_atom_cols))]))

set_default_graph = Rule('default_graph_params'
    ,query = """INSERT INTO graph_params (include_frac,group_cut,min_bo)
                VALUES (0.8,0.3,0.03) ON DUPLICATE KEY UPDATE include_frac=include_frac""")

######
populate_bonddata = Rule('populate_bonddata'
    ,query="""SELECT job_id
                    ,CONCAT('[',GROUP_CONCAT('[',atom1,',',atom2
                                            ,',',bondorder
                                            ,',',pbc_x,',',pbc_y,',',pbc_z
                                            ,']'),']') as bonddata
                  FROM bond as B
            GROUP BY job_id"""
    ,metatemp=SimpleUpdate(chargemol_job,['bonddata']))
######
mk_graph_args = ['rawstruct','include_frac','group_cut','min_bo','bonddata']

populate_graph = Rule('populate_graph'
    ,query = """SELECT GP.graph_params_id
                      ,C.job_id
                      ,S.raw AS rawstruct
                      ,GP.include_frac
                      ,GP.group_cut
                      ,GP.min_bo
                      ,C.bonddata
                      FROM chargemol_job  AS C
                        JOIN graph_params AS GP
                        JOIN struct       AS S USING(struct_id)
                      WHERE (C.job_id,GP.graph_params_id)
                              NOT IN (SELECT G.job_id,G.graph_params_id FROM graph AS G)
                            AND C.bonddata IS NOT NULL
                      GROUP BY C.job_id,GP.graph_params_id"""

    ,template   = Temp(tempfuncs = [TempFunc(mk_graph
                                               ,args = noIndex(['atoms']+mk_graph_args[1:]))
                                   ,TempFunc(json_to_traj
                                               ,'atoms'
                                            ,args = [Arg('rawstruct')])
                                   ,TempFunc(graph_to_json
                                             ,'raw'
                                             ,args = [Arg('mk_graph')])])
    ,metatemp = SimpleInsert('graph',['job_id','graph_params_id','raw']))

h_bond = Rule('h_bonds'
    ,metatemp=PureSQL(["""
        UPDATE bond as B SET B.h_bond =
        IF(bondorder between 0.05 AND 0.4, (SELECT
                             (IF(A1.element_id < A2.element_id,
                                A1.element_id = 1 AND A2.element_id = 8,
                                A1.element_id = 8 AND A2.element_id = 1))

                        FROM  atom AS A1  JOIN atom AS A2
                            WHERE A1.struct_id = B.struct_id
                            AND A1.atom_id = B.atom1
                            AND A2.struct_id = B.struct_id
                            AND A2.atom_id = B.atom2),0)
            WHERE B.job_id>0 """]))

is_tom_job = Rule('is_tom'
    ,metatemp = PureSQL(["""
            UPDATE relax_job AS R SET R.is_tom =
                (SELECT J.stordir like '%%tom%%'
                        FROM alljob AS J
                        WHERE J.job_id = R.job_id)
            WHERE R.job_id > 0 """]))

rules = [get_chargemol_struct
             ,populate_bond
             ,set_default_graph
             ,populate_bonddata
             ,populate_graph
             ,h_bond
             ,is_tom_job]
