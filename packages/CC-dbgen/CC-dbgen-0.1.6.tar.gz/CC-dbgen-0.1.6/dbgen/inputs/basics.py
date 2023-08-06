import os
from dbgen.support.datatypes.table     import Table,Col,FK,View
from dbgen.support.datatypes.temp      import Temp,TempFunc,SimpleTemp,Const
from dbgen.support.datatypes.misc      import Arg,noIndex
from dbgen.support.datatypes.metatemp  import SimpleUpsert,SimpleUpdate,SimpleInsert,PureSQL,MetaTemp,Block
from dbgen.support.datatypes.rule      import Rule
from dbgen.support.utils               import addQs,mkInsCmd
from dbgen.core.lists                  import flatten
from dbgen.support.datatypes.sqltypes  import Varchar,Decimal,Text

from dbgen.scripts.IO.get_gpaw_logfiles         import get_gpaw_logfiles
from dbgen.scripts.IO.get_qe_logfiles           import get_qe_logfiles
from dbgen.scripts.IO.get_catalog_logfiles      import get_catalog_logfiles
from dbgen.scripts.IO.get_chargemol_logfiles    import get_chargemol_logfiles
from dbgen.scripts.IO.anytraj                   import anytraj
from dbgen.scripts.IO.parse_mendeleev           import parse_mendeleev
from dbgen.scripts.IO.get_job_metadata          import get_job_metadata
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
from dbgen.scripts.Pure.Atoms.get_traj_gpaw_lazy import get_traj_gpaw_lazy
from dbgen.scripts.Pure.Atoms.get_traj_qe_lazy   import get_traj_qe_lazy
from dbgen.scripts.Pure.Atoms.get_traj_vasp_lazy import get_traj_vasp_lazy
from dbgen.scripts.Pure.Misc.dftcode_dependent  import dftcode_dependent
from dbgen.scripts.Pure.Misc.triple             import triple
from dbgen.scripts.Pure.Misc.identity           import identity
from dbgen.scripts.Pure.Misc.unzip              import unzip
from dbgen.scripts.Pure.Misc.map_               import map_
from dbgen.scripts.Pure.Misc.concat_map         import concat_map
from dbgen.scripts.Pure.Atoms.json_to_traj      import json_to_traj
from dbgen.scripts.Pure.Atoms.traj_to_json      import traj_to_json
from dbgen.scripts.Pure.Atoms.get_cell          import get_cell
from dbgen.scripts.Pure.Atoms.get_atom          import get_atom
from dbgen.scripts.Pure.Atoms.get_system_type   import get_system_type
##########################################################################################
##########################################################################################
##########################################################################################
# CONSTANTS
###########

calc_funcs = [parse_pw_gpaw,parse_pw_qe,parse_pw_vasp # type: ignore
             ,parse_xc_gpaw,parse_xc_qe,parse_xc_vasp
             ,parse_psp_gpaw,parse_psp_qe,parse_psp_vasp
             ,normalize_xc,normalize_psp,identity]

traj_funcs = [get_cell,get_atom,traj_to_json,get_traj_gpaw_lazy,get_traj_qe_lazy
             ,get_traj_vasp_lazy,identity,unzip]

cell_args = [Arg('cell',i) for i in range(9)]
cell_cols = ['a0','a1','a2','b0','b1','b2','c0','c1','c2']

##########################################################################################
roots = Table('roots'
    ,desc='Directories which are recursively searched for computation logfiles'
    ,cols = [Col('storage_id',      pk=True,auto=True)
            ,Col('root',Varchar(),  nn=True,uniq=True)
            ,Col('code',Varchar(),  nn=True,uniq=True)
            ,Col('label',Varchar(), nn=True,uniq=True)
            ,Col('active',          nn=True)])

alljob = Table('alljob'
    ,desc='DFT jobs'
    ,cols = [Col('job_id',                          pk=True,auto=True)
            ,Col('logfile',          Varchar(),         nn=True,uniq=True)
            ,Col('stordir',          Varchar(),         nn=True)
            ,Col('code',             Varchar(),         nn=True)
            ,Col('user',             Varchar())
            ,Col('timestamp')
            ,Col('working_directory',Varchar())

            ,Col('log',              Text('long'))
            ,Col('pwinp',            Text())
            ,Col('potcar',           Text('long'))
            ,Col('poscar',           Text())
            ,Col('kptcar',           Text())
            ,Col('paramdict',        Text('long'))
            ,Col('anytraj',          Text('long'))

            ,Col('job_type',         Varchar(),         ind = True)
            ,Col('job_name',         Varchar())
            ,Col('ads_catalog',      Varchar())
            ,Col('structure_catalog',Varchar())
            ,Col('deleted',                         ind=True,nn=True,default=0)])


relax_job = Table('relax_job'
        ,desc = 'Jobs that compute local minima for electronic energy'
        ,cols = [Col('job_id',        pk  = True)
                ,Col('calc_id')
                ,Col('calc_other_id')
                ,Col('reference',     ind = True)
                ,Col('is_tom')]
        ,fks  = [FK('job_id', 'alljob')
                ,FK('calc_id','calc')
                ,FK('calc_other_id','calc_other')])

traj = Table('traj'
    ,desc = 'A step in a relaxation'
    ,cols = [Col('job_id',                pk  = True)
            ,Col('traj_id',               pk  = True)
            ,Col('final',                 nn  = True)
            ,Col('struct_id',             nn  = True)
            ,Col('energy',        Decimal(),ind = True)
            ,Col('fmax',          Decimal())
            ,Col('kptden_x',      Decimal())
            ,Col('kptden_y',      Decimal())
            ,Col('kptden_z',      Decimal())]
    ,fks = [FK('job_id',   'relax_job')
           ,FK('struct_id','struct')])

#########################################
calc = Table('calc'
    ,desc='DFT calc parameters'
    ,cols = [Col('calc_id',          pk = True,auto = True)
            ,Col('dftcode',   Varchar(), nn = True,uniq = True)
            ,Col('xc',        Varchar(), nn = True,uniq = True)
            ,Col('pw',                   nn = True,uniq = True)
            ,Col('psp',       Varchar(), nn = True,uniq = True)])

element = Table('element'
    ,desc = 'ID = atomic number' # table for storing data in element.json
    ,cols = [Col('element_id',                     pk = True)
            ,Col('symbol',                 Varchar(),  nn = True)
            ,Col('atomic_weight',          Decimal(),nn = True)
            ,Col('name',                   Varchar(),  nn = True)
            ,Col('atomic_radius')
            ,Col('phase',                  Varchar())
            ,Col('group_id')
            ,Col('period')
            ,Col('pointgroup',             Varchar())
            ,Col('spacegroup')
            ,Col('evaporation_heat',        Decimal())
            ,Col('melting_point',           Decimal())
            ,Col('metallic_radius',         Decimal())
            ,Col('vdw_radius',              Decimal())
            ,Col('density',                 Decimal())
            ,Col('en_allen',                Decimal())
            ,Col('is_radioactive')
            ,Col('lattice_struct',          Varchar())
            ,Col('fusion_heat',             Decimal())
            ,Col('econf',                   Varchar())
            ,Col('covalent_radius_bragg',   Decimal())
            ,Col('geochemical_class',       Varchar())
            ,Col('abundance_crust',         Decimal())
            ,Col('heat_of_formation',       Decimal())
            ,Col('electron_affinity',       Decimal())
            ,Col('atomic_volume',           Decimal())
            ,Col('boiling_point',           Decimal())
            ,Col('proton_affinity',         Decimal())
            ,Col('covalent_radius_slater',  Decimal())
            ,Col('lattice_constant',        Decimal())
            ,Col('dipole_polarizability',   Decimal())
            ,Col('en_ghosh',                Decimal())
            ,Col('thermal_conductivity',    Decimal())
            ,Col('en_pauling',              Decimal())
            ,Col('gas_basicity',            Decimal())
            ,Col('abundance_sea',           Decimal())])
#########
cell = Table('cell'
    ,desc = 'Periodic cells defined by three vectors'
    ,cols = [Col('cell_id',             pk = True,auto = True)
            ,Col('a0',          Decimal(),nn = True,uniq = True)
            ,Col('a1',          Decimal(),nn = True,uniq = True)
            ,Col('a2',          Decimal(),nn = True,uniq = True)
            ,Col('b0',          Decimal(),nn = True,uniq = True)
            ,Col('b1',          Decimal(),nn = True,uniq = True)
            ,Col('b2',          Decimal(),nn = True,uniq = True)
            ,Col('c0',          Decimal(),nn = True,uniq = True)
            ,Col('c1',          Decimal(),nn = True,uniq = True)
            ,Col('c2',          Decimal(),nn = True,uniq = True)
            ,Col('surface_area',Decimal())
            ,Col('volume',      Decimal())
            ,Col('a',           Decimal())
            ,Col('b',           Decimal())
            ,Col('c',           Decimal())])

struct = Table('struct'
    ,desc = 'List of unique combinations of [atom] and cell'
    ,cols = [Col('struct_id',                pk  = True,auto = True)
            ,Col('cell_id',                  nn  = True)
            ,Col('raw',             Text(),  nn  = True)
            ,Col('rawhash',         Varchar(),   nn  = True,uniq = True)
            ,Col('system_type',     Varchar(),   ind = True) # used to partition subclasses
            ,Col('n_atoms')
            ,Col('n_elems')
            ,Col('composition',     Varchar())
            ,Col('composition_norm',Varchar())
            ,Col('metal_comp',      Varchar())
            ,Col('str_symbols',     Varchar())
            ,Col('str_constraints', Varchar())
            ,Col('symmetry',        Varchar())
            ,Col('pure_struct_id')
            ,Col('pure_struct_id_catalog')
            ,Col('species_id')
            ,Col('spacegroup')
            ,Col('geo_graph',       Text('long'))
            ,Col('elemental')]
    ,fks  = [FK('cell_id',       'cell')
            ,FK('pure_struct_id','pure_struct')
            ,FK('species_id','species')])

atom = Table('atom'
    ,desc = 'List of atoms in unique structs'
    ,cols = [Col('struct_id',                pk = True)
            ,Col('atom_id',                  pk = True)
            ,Col('x',            Decimal(),  nn = True)
            ,Col('y',            Decimal(),  nn = True)
            ,Col('z',            Decimal(),  nn = True)
            ,Col('constrained')
            ,Col('magmom',       Decimal())
            ,Col('tag')
            ,Col('v3')
            ,Col('v4')
            ,Col('v5')
            ,Col('v6')
            ,Col('v7')
            ,Col('v8')
            ,Col('v9')
            ,Col('v10')
            ,Col('adsorbate_id')
            ,Col('struct_adsorbate_id')
            ,Col('adsorbate_id_catalog')
            ,Col('struct_adsorbate_id_catalog')
            ,Col('layer')]
    ,fks = [FK('struct_id', 'struct')
           ,FK('element_id','element')
           ,FK(['struct_id'
               ,'adsorbate_id'
               ,'struct_adsorbate_id']
               ,'struct_adsorbate')])


trajatom = Table('trajatom'
        ,desc = "An atom considered as part of an optimization trajectory"
        ,cols = [Col('job_id',        pk=True)
                ,Col('traj_id',        pk=True)
                ,Col('struct_id',    pk=True)
                ,Col('atom_id',        pk=True)
                ,Col('fx',Decimal())
                ,Col('fy',Decimal())
                ,Col('fz',Decimal())]
        ,fks  = [FK(['job_id','traj_id'],'traj')
                ,FK(['struct_id','atom_id'],'atom')])
tables = [roots,alljob,relax_job,traj,calc,element,cell,struct,atom,trajatom]
##########################################################################################
##########################################################################################
##########################################################################################
job = View('job',"""SELECT A.job_id,A.user,A.timestamp,A.logfile,A.stordir,A.code
                          ,A.job_type,A.working_directory,A.ads_catalog,A.structure_catalog
                          ,A.deleted,A.job_name
                    FROM alljob AS A
                    WHERE NOT A.deleted""")
finaltraj = View('finaltraj','SELECT * FROM traj WHERE traj.final')


views = [job,finaltraj]
##########################################################################################
##########################################################################################
##########################################################################################

populate_gpaw_job = Rule(name = 'stray_gpaw_logfiles'
    ,query    = """SELECT R.root
                    FROM roots AS R
                    WHERE R.code = 'gpaw'
                      AND R.label = 'stray'
                      AND R.active
                     GROUP BY R.root"""
    ,template = SimpleTemp(get_gpaw_logfiles
                          ,['root']
                          ,['stordir','logfile']
                          ,{'code':Const('gpaw')})
    ,metatemp = SimpleInsert('alljob',['stordir','logfile','code']))

populate_qe_job = Rule(name = 'stray_qe_logfiles'
    ,query    = """SELECT R.root
                    FROM roots AS R
                    WHERE R.code = 'quantumespresso'
                      AND R.label = 'stray'
                      AND R.active"""
    ,template = SimpleTemp(get_qe_logfiles
                          ,['root']
                          ,['stordir','logfile']
                          ,{'code':Const('quantumespresso')})
    ,metatemp = SimpleInsert('alljob',['stordir','logfile','code']))

pop_job_cols = ['stordir','logfile','code','log','pwinp','potcar','poscar','kptcar'
               ,'paramdict']
# GROUP concat string is TOO BIG (and it's much faster without checking)
populate_catalog_job = Rule(name = 'catalog'
    ,query    = """SELECT  R.root
                    FROM roots AS R
                    WHERE R.label = 'catalog'
                      AND R.active
                    """
    ,template = SimpleTemp(get_catalog_logfiles
                          ,['root']
                          ,pop_job_cols)
    ,metatemp = SimpleInsert('alljob',pop_job_cols))

populate_chgmol_job = Rule(name = 'stray_chargemol_logfiles'
    ,query    = """SELECT  R.root
                    FROM roots AS R
                    WHERE R.code = 'chargemol'
                        AND R.label = 'stray'
                        AND R.active
                    """
    ,template = SimpleTemp(get_chargemol_logfiles
                          ,['root']
                          ,['stordir','logfile']
                          ,{'code':Const('chargemol')})
    ,metatemp = SimpleInsert('alljob',['stordir','logfile','code']))

anyTraj = Rule(name='anytraj'
    ,query    = """SELECT J.stordir,J.job_id FROM alljob AS J
                    WHERE J.anytraj is NULL AND NOT J.deleted"""
    ,template = SimpleTemp(anytraj,['stordir'],['anytraj'])
    ,metatemp = SimpleUpdate(alljob,['anytraj']))
################################################################################
mdata_cols = ['user','timestamp','working_directory'
             ,'job_type','job_name']

getJobMetadata = Rule(name = 'metadata'
    ,query    = """SELECT J.job_id,J.stordir,J.code,J.paramdict
                    FROM alljob AS J
                    WHERE J.user is null AND NOT J.deleted"""
    ,template = SimpleTemp(get_job_metadata,['stordir','code','paramdict'],mdata_cols)
    ,metatemp = SimpleUpdate(tab  = alljob
                            ,cols = mdata_cols))

################################################################################

populate_relax_calc = Rule(name='calc'
        ,query    = """SELECT relax_job.job_id,J.log,J.code AS dftcode
                        FROM relax_job
                        JOIN alljob as J USING (job_id)
                        WHERE relax_job.calc_id is null
                             AND NOT J.deleted"""
        ,template = Temp(
            constants = {f.__name__:Const(f) for f in calc_funcs}
            ,tempfuncs = [TempFunc(dftcode_dependent
                                      ,name = x
                                      ,args = noIndex(['dftcode'
                                                      ,'log'
                                                      ,'parse_%s_gpaw'%x
                                                      ,'parse_%s_qe'%x
                                                      ,'parse_%s_vasp'%x
                                                      ,'identity'
                                                      ,'identity' if x =='pw' else 'normalize_%s'%x]))
                                                      for x in ['pw','xc','psp']])

        ,metatemp = SimpleUpsert(ins_tab   = calc
                                ,ins_cols  = ["dftcode","xc","pw","psp"]
                                ,fk_tab    = relax_job))
populate_relax_job = Rule(name = 'relax_job'
        ,metatemp = PureSQL([
        """ INSERT INTO relax_job (job_id)
                SELECT J.job_id FROM alljob AS J
                    WHERE J.job_type IN ('relax','latticeopt','vcrelax')
                    AND J.job_id NOT IN (SELECT R.job_id from relax_job AS R)
                    AND NOT J.deleted"""]))



# if any ionic steps are in the traj table, then we assume all 4 tables have been taken care of
populate_traj = Rule(name='traj'
    ,query = """SELECT R.job_id,J.code AS dftcode,J.log,J.anytraj,J.poscar,J.stordir
                 FROM relax_job AS R JOIN alljob AS J USING (job_id)
                 WHERE R.job_id NOT IN (SELECT traj.job_id FROM traj)
                 AND J.code != 'vasp' # TEMPORARY THING
                 AND NOT J.deleted"""

    ,template = Temp(constants = {f.__name__:Const(f) for f in traj_funcs}
        ,tempfuncs=[
              TempFunc(triple
                      ,'anytraj_log_poscar'
                      ,args = noIndex(['anytraj','log','poscar']))


              ,TempFunc(dftcode_dependent
                       ,name = 'get_traj'
                       ,args = noIndex(['dftcode'
                                  ,'anytraj_log_poscar'
                                  ,'get_traj_gpaw_lazy'
                                  ,'get_traj_qe_lazy'
                                  ,'get_traj_vasp_lazy'
                                  ,'identity'
                                  ,'unzip'])) # returns ([ASEATOMS]m,[STEPNUM]m,[ENERGY]m,[TRAJATOMLIST]m)
               ,TempFunc(map_
                        ,name = 'cell'
                        ,args = noIndex(['get_cell','structs_few'])) # returns ([ax]m,[ay]m,...)
               ,TempFunc(map_
                        ,name = 'structs_few'
                        ,args = [Arg('traj_to_json')
                                ,Arg('get_traj', 0)]) # returns [raw_json]m
               ,TempFunc(concat_map
                        ,name = 'atoms'
                        ,args = noIndex(['get_atom','structs_few'])) # returns ([ASEATOMS]n,[Ind]n,[ELEMENT]n,[X]n,[Y]n,...)
               ,TempFunc(identity
                        ,name = 'structs_many'
                        ,args = [Arg('atoms', 0)])# returns [raw_json]n
                ,TempFunc(flatten
                         ,name = 'flattened_trajatoms'
                         ,args = [Arg('get_traj',3)])  # [STEPNUM,Ind,FX,FY,FZ]n
                ,TempFunc(unzip
                         ,'trajatoms'
                         ,args=[Arg('flattened_trajatoms')])]) # ([STEPNUM]n,[Ind]n,[FX]n,[FY]n,[FZ]n)

    ,metatemp = MetaTemp([
        Block(name = 'insert_cell'
             ,text = mkInsCmd('cell',cell_cols,sqlite=False)
             ,args = cell_args)

       ,Block(name = 'query_cell'
             ,text = ('SELECT C.cell_id FROM cell AS C WHERE '
                     +addQs(['C.%s'%x for x in cell_cols],' AND '))
             ,args = cell_args)

       ,Block(name = 'insert_struct'
             ,text = """INSERT INTO struct (raw,rawhash,cell_id)
                           VALUES (%s,SHA2(%s,512),%s)
                        ON DUPLICATE KEY UPDATE cell_id=cell_id"""
             ,args = [Arg('structs_few')
                      ,Arg('structs_few')
                     ,Arg('query_cell',0)])

       ,Block(name = 'query_struct_few'
             ,text = 'SELECT S.struct_id FROM struct AS S WHERE S.rawhash = SHA2(%s,512)'
             ,args = [Arg('structs_few')])

       ,Block(name = 'query_struct_many'
             ,text = 'SELECT S.struct_id FROM struct AS S WHERE S.rawhash = SHA2(%s,512)'
             ,args = [Arg('structs_many')])

       ,Block(name = 'insert_atom'
             ,text = mkInsCmd('atom',['struct_id','atom_id','element_id'
                                  ,'x','y','z','constrained','magmom','tag']
                            ,sqlite=False)
             ,args = [Arg('query_struct_many')]
                    +[Arg('atoms',i) for i in range(1,9)])

     ,Block(name = 'insert_traj'
           ,text = mkInsCmd('traj',['job_id','traj_id','struct_id','energy','final'],sqlite=False)
           ,args = [Arg('job_id')
                   ,Arg('get_traj',1)
                   ,Arg('query_struct_few')
                   ,Arg('get_traj',2)
                   ,Arg('get_traj',4)])

    ,Block(name = 'insert_trajatom'
          ,text = mkInsCmd('trajatom',['job_id','traj_id','struct_id','atom_id','fx','fy','fz'],sqlite=False)
          ,args = [Arg('job_id')
                  ,Arg('trajatoms',0)
                  ,Arg('query_struct_many')]
                 +[Arg('trajatoms',i) for i in range(1,5)])]))

allcols = ['element_id', 'symbol', 'name', 'atomic_weight','atomic_radius'
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

populate_element = Rule(name='element'
    ,template = SimpleTemp(parse_mendeleev,[],allcols)
    ,metatemp = SimpleInsert('element',allcols))

sys_type = Rule(name='systype'
    ,query      = """SELECT S.struct_id,S.raw
                     FROM struct AS S
                     WHERE S.system_type IS NULL"""
    ,template   = Temp(tempfuncs=[TempFunc(get_system_type
                                          ,name = 'system_type'
                                          ,args = [Arg('json_to_traj')])
                                 ,TempFunc(json_to_traj
                                          ,args = [Arg('raw')])])
    ,metatemp   = SimpleUpdate(tab  = struct
                              ,cols = ['system_type']))


cell_info = Rule(name='cell'
    ,metatemp=PureSQL(["""UPDATE cell AS C SET surface_area = SQRT((C.a0*C.b2-C.a2*C.b1) * (C.a1*C.b2 - C.a2*C.b1)
                                                                 +(C.a0*C.b2-C.a2*C.b0) * (C.a0*C.b2 - C.a2*C.b0)
                                                                 +(C.a0*C.b1-C.a1*C.b0) * (C.a0*C.b1 - C.a1*C.b0))
                                              ,volume = C.a0*(C.b1*C.c2-C.b2*C.c1)
                                                       -C.a1*(C.b0*C.c2-C.b2*C.c0)
                                                       +C.a2*(C.b0*C.c1-C.b1*C.c0)
                                              ,a = SQRT(C.a0*C.a0+C.a1*C.a1+C.a2*C.a2)
                                              ,b = SQRT(C.b0*C.b0+C.b1*C.b1+C.b2*C.b2)
                                              ,c = SQRT(C.c0*C.c0+C.c1*C.c1+C.c2*C.c2)
                        WHERE C.cell_id > 0"""]))
n_atoms = Rule(name='n_atoms'
    ,metatemp=PureSQL(["""UPDATE struct SET n_atoms = (SELECT count(1)
                                FROM atom WHERE atom.struct_id=struct.struct_id
                                GROUP BY atom.struct_id)
                          WHERE struct_id > 0"""

                    ,"""UPDATE struct SET n_elems = (SELECT count(1)
                                    FROM struct_composition AS C WHERE C.struct_id=struct.struct_id
                                    GROUP BY C.struct_id)
                                    WHERE struct_id > 0"""]))

with open(os.path.join(logfile_lists.__path__._path[0],'sherlock_ksb.txt'),'r') as f:
    rootdata  = [l.split() for l in f.readlines() if '#' not in l and l.strip()!='']

pop_storage= Rule('root'
    ,metatemp=PureSQL(["""INSERT INTO roots (root,code,label,active) VALUES ('%s','%s','%s',1)
                        ON DUPLICATE KEY UPDATE storage_id=storage_id
                        """%(pth,code,label) for pth,code,label in rootdata]))

rules = [pop_storage
        ,populate_gpaw_job
        ,populate_qe_job
        ,populate_catalog_job
        ,populate_chgmol_job
        ,getJobMetadata
        ,populate_relax_calc
        ,populate_relax_job
        ,populate_traj
        ,populate_element
        ,sys_type
        ,cell_info
        ,n_atoms
        ,anyTraj]
