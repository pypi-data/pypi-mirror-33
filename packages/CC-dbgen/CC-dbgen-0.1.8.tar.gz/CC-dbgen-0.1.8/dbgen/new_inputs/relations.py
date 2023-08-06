# Internal Modules
from dbgen.support.datatypes.sqltypes     import Varchar,Date
from dbgen.support.datatypes.select       import Select
from dbgen.support.datatypes.temp         import SimpleTemp,SimplePipe,Const
from dbgen.support.datatypes.object       import Object,Attr,Universe
from dbgen.support.datatypes.relation     import Relation
from dbgen.support.datatypes.insertupdate import Insert
from dbgen.support.datatypes.constraint   import NULL,IN,HAS
from dbgen.support.datatypes.temp         import Temp,TempFunc
from dbgen.support.datatypes.misc         import Arg,noIndex

from dbgen.new_inputs.objects             import *
from dbgen.core.lists                     import flatten

from dbgen.scripts.IO.get_catalog_logfiles      import get_catalog_logfiles
from dbgen.scripts.IO.anytraj                   import anytraj
from dbgen.scripts.IO.parse_mendeleev           import parse_mendeleev
from dbgen.scripts.IO.get_job_metadata          import get_job_metadata
from dbgen.scripts.Pure.Misc.dftcode_dependent  import dftcode_dependent
from dbgen.scripts.Pure.Misc.identity           import identity
from dbgen.scripts.Pure.Atoms.cell_info         import cell_info
from dbgen.scripts.Pure.Atoms.json_to_traj      import json_to_traj
from dbgen.scripts.Pure.Atoms.get_system_type   import get_system_type
from dbgen.scripts.Pure.Load.populate_storage   import populate_storage
from dbgen.scripts.Pure.Load.parse_pw_gpaw      import parse_pw_gpaw
from dbgen.scripts.Pure.Load.parse_pw_qe        import parse_pw_qe
from dbgen.scripts.Pure.Load.parse_pw_vasp      import parse_pw_vasp
from dbgen.scripts.Pure.Load.parse_xc_gpaw      import parse_xc_gpaw
from dbgen.scripts.Pure.Load.parse_xc_qe        import parse_xc_qe
from dbgen.scripts.Pure.Load.parse_xc_vasp      import parse_xc_vasp
from dbgen.scripts.Pure.Load.parse_psp_gpaw     import parse_psp_gpaw
from dbgen.scripts.Pure.Load.parse_psp_qe       import parse_psp_qe
from dbgen.scripts.Pure.Load.parse_psp_vasp     import parse_psp_vasp
from dbgen.scripts.Pure.Load.normalize_xc       import normalize_xc
from dbgen.scripts.Pure.Load.normalize_psp      import normalize_psp

##############################################################################

# Constants
#----------
pop_job_cols = ['stordir','logfile','code','log','pwinp'
               ,'potcar','poscar','kptcar','paramdict']

mdata_input = ['stordir','code','paramdict']
mdata_cols  = ['user','timestamp','working_directory'
              ,'job_type','job_name']

elem_cols  =  [ 'element_id', 'symbol', 'name', 'atomic_weight','atomic_radius'
              , 'phase','evaporation_heat', 'pointgroup','spacegroup'
              , 'melting_point', 'metallic_radius', 'vdw_radius'
              , 'density', 'en_allen', 'is_radioactive'
              , 'lattice_struct' , 'fusion_heat'
              , 'econf', 'period', 'covalent_radius_bragg'
              , 'geochemical_class', 'abundance_crust', 'heat_of_formation'
              , 'electron_affinity', 'atomic_volume',  'boiling_point'
              , 'proton_affinity', 'covalent_radius_slater'
              , 'lattice_constant', 'dipole_polarizability'
              , 'en_ghosh', 'thermal_conductivity', 'group_id', 'en_pauling'
              , 'gas_basicity','abundance_sea']

cell_cols = ['a0','a1','a2','b0','b1','b2','c0','c1','c2']


dfts       = ['gpaw','qe','vasp']
parsed     = ['pw',  'xc','psp']

calc_funcs = [parse_pw_gpaw,parse_pw_qe,parse_pw_vasp # type: ignore
             ,parse_xc_gpaw,parse_xc_qe,parse_xc_vasp
             ,parse_psp_gpaw,parse_psp_qe,parse_psp_vasp
             ,normalize_xc,normalize_psp,identity]

##############################################################################

relax_calc_func = Temp(constants = {f.__name__:Const(f) for f in calc_funcs}
    ,tempfuncs = [TempFunc(func = dftcode_dependent
                          ,name = x
                          ,args = noIndex(['dftcode'
                                          ,'log'
                                          ,'parse_%s_gpaw'%x
                                          ,'parse_%s_qe'%x
                                          ,'parse_%s_vasp'%x
                                          ,'identity'
                                          ,'identity' if x =='pw' else 'normalize_%s'%x]))
                    for x in parsed])

########################################################################
loading_relations = [
    Relation(name    = 'catalog'
            ,select  = uni.select(attrs       = [roots.root]                 # type: ignore
                             ,constraints = [roots.label == "'catalog'"  # type: ignore
                                            ,roots.active ==1 ])         # type: ignore
            ,func    = SimpleTemp(func    = get_catalog_logfiles
                                 ,inputs  = ['root']
                                 ,outputs = pop_job_cols)
            ,inserts = [alljob.insert(schema,pop_job_cols)])

   ,Relation(name    = 'populate_storage'
            ,func    = SimpleTemp(func    = populate_storage
                                 ,outputs = ['root','code','label'])
            ,inserts = [roots.insert(schema,['root','code','label'])])

   ,Relation(name    = 'job_metadata'
            ,select  = Select(schema
                             ,attrs       = alljob.select(schema,mdata_input)
                             ,constraints = [NULL(alljob.user)     # type: ignore
                                            ,alljob.deleted==0])   # type: ignore
            ,func    = SimpleTemp(func    = get_job_metadata
                                 ,inputs  = mdata_input
                                 ,outputs = mdata_cols)
            ,inserts = [alljob.update(schema,mdata_cols)])

   ,Relation(name   = 'anytraj'
            ,select = Select(schema
                             ,attrs       = alljob.select(schema,['stordir'])
                             ,constraints = [NULL(alljob.anytraj)  # type: ignore
                                            ,alljob.deleted==0])   # type: ignore
            ,func   = SimpleTemp(anytraj,['stordir'],['anytraj'])
            ,inserts= [alljob.update(schema,['anytraj'])])

    ,Relation(name = 'mendeleev'
             ,func = SimpleTemp(parse_mendeleev,outputs = elem_cols)
             ,inserts = [element.insert(schema,elem_cols)])

    ,Relation(name ='cell_info'
             ,select = Select(schema
                             ,attrs = cell.select(schema,cell_cols))
             ,func = SimpleTemp(cell_info,cell_cols,['surface_area','volume'])
             ,inserts = [cell.insert(schema,['surface_area','volume'])])

   ,Relation(name    = 'relax_calc'
            ,select  = Select(schema
                             ,attrs = alljob.select(schema,['log','code'])
                             ,constraints = [alljob.deleted == 0       # type: ignore
                                            ,HASNT(relax_job,calc)]) # type: ignore
            ,func    = relax_calc_func
            ,inserts = [calc.insert(schema,['dftcode','pw','xc','psp'])
                       ,relax_job.update_component(schema,calc)])

   ,Relation(name = 'systype'
            ,select = Select(schema
                            ,attrs       = [struct.raw]                 # type: ignore
                            ,constraints = [NULL(struct.system_type)])  # type: ignore
            ,func = SimplePipe([json_to_traj,get_system_type]
                               ,inputs  = ['raw']
                               ,outputs = ['system_type'])
            ,inserts = [struct.update(schema,['system_type'])])

   ,Relation(name    = 'relax_job'
            ,select  = Select(schema
                             ,attrs       = alljob.select(schema)
                             ,constraints = [IN(alljob.job_type   # type: ignore
                                            ,["'relax'","'latticeopt'","'vcrelax'"])])
            ,inserts = [relax_job.insert(schema)])

]

# if any ionic steps are in the traj table, then we assume all 4 tables have been
# taken care of
# populate_traj = Rule(name='populate_struct_traj_atom_cell'
#     ,query = """SELECT R.job_id,J.code AS dftcode,J.log,J.anytraj,J.poscar,J.stordir
#                  FROM relax_job AS R JOIN alljob AS J USING (job_id)
#                  WHERE R.job_id NOT IN (SELECT traj.job_id FROM traj)
#                  AND J.code != 'vasp' # TEMPORARY THING
#                  AND NOT J.deleted"""
#
#     ,template = Temp(constants = {'get_cell'              : Const('get_cell')
#                                    ,'get_atom'              : Const('get_atom')
#                                    ,'traj_to_json'          : Const('traj_to_json')
#                                    ,'get_traj_gpaw%s'%laz   : Const('get_traj_gpaw%s'%laz)
#                                    ,'get_traj_qe%s'%laz     : Const('get_traj_qe%s'%laz)
#                                    ,'get_traj_vasp%s'%laz   : Const('get_traj_vasp%s'%laz)
#                                    ,'identity'              : Const('identity')
#                                    ,'unzip'                 : Const('unzip')}
#         ,tempfuncs=[
#               TempFunc(triple'
#                       ,'anytraj_log_poscar'
#                       ,args = noIndex(['anytraj','log','poscar']))
#
#
#               ,TempFunc(dftcode_dependent'
#                        ,name = 'get_traj'
#                        ,args = noIndex(['dftcode'
#                                   ,'anytraj_log_poscar'
#                                   ,'get_traj_gpaw%s'%laz
#                                   ,'get_traj_qe%s'%laz
#                                   ,'get_traj_vasp%s'%laz
#                                   ,'identity'
#                                   ,'unzip'])) # returns ([ASEATOMS]m,[STEPNUM]m,[ENERGY]m,[TRAJATOMLIST]m)
#                ,TempFunc(map'
#                         ,name = 'cell'
#                         ,args = noIndex(['get_cell','structs_few'])) # returns ([ax]m,[ay]m,...)
#                ,TempFunc(map'
#                         ,name = 'structs_few'
#                         ,args = [Arg('traj_to_json')
#                                 ,Arg('get_traj', 0)]) # returns [raw_json]m
#                ,TempFunc(concat_map'
#                         ,name = 'atoms'
#                         ,args = noIndex(['get_atom','structs_few'])) # returns ([ASEATOMS]n,[Ind]n,[ELEMENT]n,[X]n,[Y]n,...)
#                ,TempFunc(identity'
#                         ,name = 'structs_many'
#                         ,args = [Arg('atoms', 0)])# returns [raw_json]n
#                 ,TempFunc(flatten'
#                          ,name = 'flattened_trajatoms'
#                          ,args = [Arg('get_traj',3)])  # [STEPNUM,Ind,FX,FY,FZ]n
#                 ,TempFunc(unzip'
#                          ,'trajatoms'
#                          ,args=[Arg('flattened_trajatoms')])]) # ([STEPNUM]n,[Ind]n,[FX]n,[FY]n,[FZ]n)
#
#     ,metatemp = MetaTemp([
#         Block(name = 'insert_cell'
#              ,text = mkInsCmd('cell',cell_cols,sqlite=False)
#              ,args = cell_args)
#
#        ,Block(name = 'query_cell'
#              ,text = ('SELECT C.cell_id FROM cell AS C WHERE '
#                      +addQs(['C.%s'%x for x in cell_cols],' AND '))
#              ,args = cell_args)
#
#        ,Block(name = 'insert_struct'
#              ,text = """INSERT INTO struct (raw,rawhash,cell_id)
#                            VALUES (%s,SHA2(%s,512),%s)
#                         ON DUPLICATE KEY UPDATE cell_id=cell_id"""
#              ,args = [Arg('structs_few')
#                       ,Arg('structs_few')
#                      ,Arg('query_cell',0)])
#
#        ,Block(name = 'query_struct_few'
#              ,text = 'SELECT S.struct_id FROM struct AS S WHERE S.rawhash = SHA2(%s,512)'
#              ,args = [Arg('structs_few')])
#
#        ,Block(name = 'query_struct_many'
#              ,text = 'SELECT S.struct_id FROM struct AS S WHERE S.rawhash = SHA2(%s,512)'
#              ,args = [Arg('structs_many')])
#
#        ,Block(name = 'insert_atom'
#              ,text = mkInsCmd('atom',['struct_id','atom_id','element_id'
#                                   ,'x','y','z','constrained','magmom','tag']
#                             ,sqlite=False)
#              ,args = [Arg('query_struct_many')]
#                     +[Arg('atoms',i) for i in range(1,9)])
#
#      ,Block(name = 'insert_traj'
#            ,text = mkInsCmd('traj',['job_id','traj_id','struct_id','energy','final'],sqlite=False)
#            ,args = [Arg('job_id')
#                    ,Arg('get_traj',1)
#                    ,Arg('query_struct_few')
#                    ,Arg('get_traj',2)
#                    ,Arg('get_traj',4)])
#
#     ,Block(name = 'insert_trajatom'
#           ,text = mkInsCmd('trajatom',['job_id','traj_id','struct_id','atom_id','fx','fy','fz'],sqlite=False)
#           ,args = [Arg('job_id')
#                   ,Arg('trajatoms',0)
#                   ,Arg('query_struct_many')]
#                  +[Arg('trajatoms',i) for i in range(1,5)])]))

relations = loading_relations
