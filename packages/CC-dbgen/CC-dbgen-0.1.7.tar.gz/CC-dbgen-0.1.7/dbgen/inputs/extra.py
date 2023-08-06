# External Modules
from os import environ
# Internal Modules
from dbgen.support.datatypes.table     import Table,Col,FK
from dbgen.support.datatypes.table     import Table,Col,FK
from dbgen.support.datatypes.table     import Table,Col,FK,View
from dbgen.support.datatypes.temp      import Temp,TempFunc,Const,SimpleTemp
from dbgen.support.datatypes.misc      import Arg,noIndex
from dbgen.support.datatypes.metatemp  import PureSQL,SimpleUpdate,MetaTemp,Block,SimpleInsert
from dbgen.support.datatypes.rule      import Rule
from dbgen.inputs.basics               import struct,traj,atom
from dbgen.core.lists                  import flatten,merge_dicts
from dbgen.support.datatypes.sqltypes  import Varchar,Decimal

from dbgen.scripts.Pure.Load.get_dipol_gpaw         import get_dipol_gpaw
from dbgen.scripts.Pure.Load.get_dipol_qe           import get_dipol_qe
from dbgen.scripts.Pure.Load.get_dipol_vasp         import get_dipol_vasp
from dbgen.scripts.Pure.Load.get_gamma_gpaw         import get_gamma_gpaw
from dbgen.scripts.Pure.Load.get_gamma_qe           import get_gamma_qe
from dbgen.scripts.Pure.Load.get_gamma_vasp         import get_gamma_vasp
from dbgen.scripts.Pure.Load.get_econv_gpaw         import get_econv_gpaw
from dbgen.scripts.Pure.Load.get_econv_qe           import get_econv_qe
from dbgen.scripts.Pure.Load.get_econv_vasp         import get_econv_vasp
from dbgen.scripts.Pure.Load.get_sigma_gpaw         import get_sigma_gpaw
from dbgen.scripts.Pure.Load.get_sigma_qe           import get_sigma_qe
from dbgen.scripts.Pure.Load.get_sigma_vasp         import get_sigma_vasp
from dbgen.scripts.Pure.Load.get_mixing_gpaw        import get_mixing_gpaw
from dbgen.scripts.Pure.Load.get_mixing_qe          import get_mixing_qe
from dbgen.scripts.Pure.Load.get_mixing_vasp        import get_mixing_vasp
from dbgen.scripts.Pure.Load.get_nbands_gpaw        import get_nbands_gpaw
from dbgen.scripts.Pure.Load.get_nbands_qe          import get_nbands_qe
from dbgen.scripts.Pure.Load.get_nbands_vasp        import get_nbands_vasp
from dbgen.scripts.Pure.Load.get_nmix_gpaw          import get_nmix_gpaw
from dbgen.scripts.Pure.Load.get_nmix_qe            import get_nmix_qe
from dbgen.scripts.Pure.Load.get_nmix_vasp          import get_nmix_vasp
from dbgen.scripts.Pure.Load.get_diag_gpaw          import get_diag_gpaw
from dbgen.scripts.Pure.Load.get_diag_qe            import get_diag_qe
from dbgen.scripts.Pure.Load.get_diag_vasp          import get_diag_vasp
from dbgen.scripts.Pure.Load.get_spinpol_gpaw       import get_spinpol_gpaw
from dbgen.scripts.Pure.Load.get_spinpol_qe         import get_spinpol_qe
from dbgen.scripts.Pure.Load.get_spinpol_vasp       import get_spinpol_vasp
from dbgen.scripts.Pure.Load.get_dipole_gpaw        import get_dipole_gpaw
from dbgen.scripts.Pure.Load.get_dipole_qe          import get_dipole_qe
from dbgen.scripts.Pure.Load.get_dipole_vasp        import get_dipole_vasp
from dbgen.scripts.Pure.Load.get_maxstep_gpaw       import get_maxstep_gpaw
from dbgen.scripts.Pure.Load.get_maxstep_qe         import get_maxstep_qe
from dbgen.scripts.Pure.Load.get_maxstep_vasp       import get_maxstep_vasp

from dbgen.scripts.Pure.Load.get_kpts_gpaw          import get_kpts_gpaw
from dbgen.scripts.Pure.Load.get_kpts_qe            import get_kpts_qe
from dbgen.scripts.Pure.Load.get_kpts_vasp          import get_kpts_vasp
from dbgen.scripts.Pure.Misc.dftcode_dependent      import dftcode_dependent
from dbgen.scripts.Pure.Misc.identity               import identity
from dbgen.scripts.Pure.Misc.get                    import get
from dbgen.scripts.Pure.Misc.flatten                import flatten
from dbgen.scripts.Pure.Misc.map_                   import map_
from dbgen.scripts.Pure.Misc.pair                   import pair
from dbgen.scripts.Pure.Misc.triple                 import triple
from dbgen.scripts.Pure.Atoms.get_voronoi           import get_voronoi
from dbgen.scripts.Pure.Atoms.get_pointgroup        import get_pointgroup
from dbgen.scripts.Pure.Atoms.get_spacegroup        import get_spacegroup
from dbgen.scripts.Pure.Atoms.json_to_traj          import json_to_traj
from dbgen.scripts.Pure.Atoms.get_vacuum            import get_vacuum
from dbgen.scripts.Pure.Load.load_comp              import load_comp
from dbgen.scripts.Pure.Load.get_vasp_key           import get_vasp_key
from dbgen.scripts.Pure.Load.get_dw                 import get_dw
from dbgen.scripts.Pure.Load.get_cell_dofree        import get_cell_dofree
from dbgen.scripts.Pure.Load.get_cell_factor        import get_cell_factor
from dbgen.scripts.Pure.Load.get_mixtype            import get_mixtype
from dbgen.scripts.Pure.Load.get_kptden             import get_kptden
from dbgen.scripts.Pure.Graph.mk_graph              import mk_graph
from dbgen.scripts.Pure.Graph.layers                import layers
from dbgen.scripts.Pure.Graph.geometric             import geometric
from dbgen.scripts.Pure.Graph.graph_to_json         import graph_to_json
from dbgen.scripts.Pure.Graph.json_to_graph         import json_to_graph

################################################################
################################################################
################################################################
# CONSTANTS
###########
pypth = environ['DBGEN_ROOT']+'/scripts/'

dfts         = ['gpaw','qe','vasp']
other_cols = ['dipol','gamma','econv','sigma','mixing','nbands'
             ,'nmix','diag','spinpol','dipole','maxstep','kpts']
cell_cols = ['a0','a1','a2','b0','b1','b2','c0','c1','c2']



get_fns = [get_dipol_gpaw,get_dipol_qe,get_dipol_vasp,get_gamma_gpaw
          ,get_gamma_qe,get_gamma_vasp,get_econv_gpaw,get_econv_qe,get_econv_vasp
          ,get_sigma_gpaw,get_sigma_qe,get_sigma_vasp,get_mixing_gpaw
          ,get_mixing_qe,get_mixing_vasp,get_nbands_gpaw,get_nbands_qe,get_nbands_vasp
          ,get_nmix_gpaw,get_nmix_qe,get_nmix_vasp,get_diag_gpaw,get_diag_qe,get_diag_vasp
          ,get_spinpol_gpaw,get_spinpol_qe,get_spinpol_vasp,get_dipole_gpaw
          ,get_dipole_qe,get_dipole_vasp,get_maxstep_gpaw,get_maxstep_qe,get_maxstep_vasp
          ,get_kpts_gpaw,get_kpts_qe,get_kpts_vasp]

################################################################
################################################################
################################################################

################################################################
################################################################
################################################################
struct_composition = Table('struct_composition'
        ,desc = 'Chemical Composition of a structure'
        ,cols = [Col('struct_id',             pk=True)
                ,Col('element_id',            pk=True)
                ,Col('has_fixed',             nn=True)
                ,Col('count',                 nn=True)
                ,Col('count_fixed',           nn=True)
                ,Col('count_norm',            nn=True)
                ,Col('frac',        Decimal(),nn=True)
                ,Col('frac_fixed',  Decimal(),nn=True)
                ,Col('fixed_norm',            nn=True)
                ]
        ,fks = [FK('struct_id', 'struct')
               ,FK('element_id','element')])

################################################################
surface = Table('surface'
        ,desc = 'Subclass of struct'
        ,cols = [Col('struct_id', pk=True)
                ,Col('vacuum',     Decimal())
                ,Col('pure_struct_id') # underlying structure
                ,Col('facet_h')
                ,Col('facet_k')
                ,Col('facet_l')
                ,Col('pure_struct_id_catalog')
                ,Col('facet_h_catalog')
                ,Col('facet_k_catalog')
                ,Col('facet_l_catalog')
                ]
        ,fks=[FK('struct_id','struct')
             ,FK('pure_struct_id','pure_struct')
             ,FK('pure_struct_id_catalog','pure_struct','pure_struct_id')])

bulk = Table('bulk'
        ,desc = 'Subclass of struct'
        ,cols = [Col('struct_id',    pk=True)
                ,Col('pure_struct_id_catalog')]
        ,fks=[FK('struct_id','struct')])

molecule = Table('molecule'
        ,desc = 'Subclass of struct'
        ,cols = [Col('struct_id',        pk=True)
                ,Col('pointgroup',  Varchar())]
        ,fks=[FK('struct_id','struct')])

########################################################################

################################################################################


similar_struct= Table('similar_struct'
    ,desc = "Store a precomputation for identifying related jobs"
    ,cols = [Col('struct_id',pk=True)
            ,Col('struct_id2',pk=True)]
    ,fks  = [FK('struct_id','struct')
            ,FK('struct_id2','struct','struct_id')])

############################################################################

calc_other = Table('calc_other'
        ,desc = """Less important DFT Calculator Parameters"""
        ,cols = [Col('calc_other_id',pk=True,auto=True)
                ,Col("kx")
                ,Col("ky")
                ,Col("kz")
                ,Col("fmax",            Decimal())
                ,Col("econv",           Decimal(10,7))
                ,Col("dw")
                ,Col("sigma",           Decimal(10,7))
                ,Col("nbands")
                ,Col("mixing",          Decimal())
                ,Col("nmix")
                ,Col("xtol",            Decimal(10,7))
                ,Col("strain",          Decimal())
                ,Col("gga",             Varchar())
                ,Col("luse_vdw")
                ,Col("zab_vdw",         Decimal())
                ,Col("nelmdl")
                ,Col("gamma")
                ,Col("dipol",           Varchar())
                ,Col("algo",            Varchar())
                ,Col("ibrion")
                ,Col("prec",            Varchar())
                ,Col("ionic_steps")
                ,Col("lreal",           Varchar())
                ,Col("lvhar")
                ,Col("diag",            Varchar())
                ,Col("spinpol")
                ,Col("dipole")
                ,Col("maxstep")
                ,Col("delta",           Decimal())
                ,Col("mixingtype",      Varchar())
                ,Col("bonded_inds",     Varchar())
                ,Col("energy_cut_off",  Decimal())
                ,Col("step_size",       Decimal())
                ,Col("spring",          Decimal())
                ,Col('cell_dofree',     Varchar())
                ,Col('cell_factor',     Decimal())
                ,Col("kpts",            Varchar())])


#############################################################################
vib_job = Table('vib_job'
        ,desc = 'Jobs that compute vibrational modes for a struct'
        ,cols = [Col('job_id',pk=True)
                ,Col('calc_id')
                ,Col('struct_id')]
        ,fks  = [FK('job_id',    'alljob')
                ,FK('calc_id',    'calc')
                ,FK('struct_id','struct')])

dos_job = Table('dos_job'
        ,desc = 'Jobs that compute density of states for a struct'
        ,cols = [Col('job_id',pk=True)
                ,Col('calc_id')
                ,Col('struct_id')]
        ,fks  = [FK('job_id',    'alljob')
                ,FK('calc_id',    'calc')
                ,FK('struct_id','struct')])

neb_job = Table('neb_job'
        ,desc = 'Jobs that compute NEB between two structures'
        ,cols = [Col('job_id',pk=True)
                ,Col('calc_id')
                ,Col('init_struct_id')
                ,Col('final_struct_id')]
        ,fks  = [FK('job_id',    'alljob')
                ,FK('calc_id',    'calc')
                ,FK('init_struct_id','struct','struct_id')
                ,FK('final_struct_id','struct','struct_id')])

bulkmod_job = Table('bulkmod_job'
        ,desc = 'Jobs that compute bulk modulus for a struct'
        ,cols = [Col('job_id',        pk=True)
                ,Col('calc_id')
                ,Col('struct_id')
                ,Col('bulkmod',    Decimal())]
        ,fks  = [FK('job_id',    'alljob')
                ,FK('calc_id',  'calc')
                ,FK('struct_id','struct')])

tables = [struct_composition
         ,surface
         ,bulk
         ,molecule
         ,calc_other
         ,similar_struct
         ,dos_job
         ,vib_job
         ,neb_job
         ,bulkmod_job]
##############################################################################
##############################################################################
##############################################################################


geograph = Rule('geograph'
    ,query    = """SELECT S.struct_id,S.raw from struct AS S WHERE S.geo_graph IS NULL"""
    ,template = Temp(tempfuncs = [TempFunc(geometric
                                         ,args=[Arg('json_to_traj')])
                                ,TempFunc(json_to_traj,args=[Arg('raw')])
                                ,TempFunc(graph_to_json
                                         ,'geo_graph'
                                         ,args=[Arg('mk_graph')])
                                ,TempFunc(mk_graph
                                         ,args = noIndex(['json_to_traj'
                                                           ,'include_frac'
                                                         ,'group_cut'
                                                         ,'min_bo'
                                                         ,'geometric']))]
                    ,constants = {'include_frac': Const(0.8)
                                 ,'group_cut'     : Const(0.3)
                                 ,'min_bo'         : Const(0.03)})
    ,metatemp = SimpleUpdate(struct,['geo_graph']))


elemental = Rule('elemental'
    ,metatemp=PureSQL(["""UPDATE struct AS S SET S.elemental =
                             S.n_atoms=1 AND S.system_type = 'molecule'
                             WHERE S.struct_id >0"""]))
fmax = Rule('fmax'
    ,metatemp=PureSQL(["""UPDATE traj AS T SET T.fmax =

                (SELECT
                    MAX(SQRT(TA.fx * TA.fx + TA.fy * TA.fy + TA.fz * TA.fz)) AS fmax
                FROM
                    traj AS T2
                JOIN
                    trajatom AS TA USING (job_id , traj_id , struct_id)
                JOIN
                    atom AS A USING (struct_id , atom_id)
                WHERE
                    A.constrained = 0
                GROUP BY job_id,traj_id)


                WHERE
                T2.job_id=T.job_id AND T2.traj_id=T.traj_id
                AND T.job_id >0 AND T.struct_id > 0"""]))

voronoi = Rule('voronoi'
    ,query      = """SELECT DISTINCT S.struct_id,S.raw
                     FROM struct AS S JOIN atom AS A USING (struct_id)
                     WHERE A.v3 IS NULL"""
    ,template     = Temp(tempfuncs=[TempFunc(get_voronoi
                                          ,args = [Arg('json_to_traj')])
                                 ,TempFunc(json_to_traj
                                          ,args = [Arg('raw')])])
    ,metatemp   = MetaTemp([Block(name='update_voronoi'
                                ,text="""UPDATE atom SET v3=%s,v4=%s,v5=%s,v6=%s
                                                        ,v7=%s,v8=%s,v9=%s,v10=%s
                                        WHERE struct_id = %s AND atom_id = %s"""
                                ,args = [Arg('get_voronoi',i) for i in range(1,9)]
                                        +[Arg('struct_id'),Arg('get_voronoi',0)])]))

populate_subjobs = Rule(name = 'subjobs'
        ,metatemp = PureSQL([
        """ INSERT INTO bulkmod_job (job_id)
                SELECT J.job_id FROM alljob AS J
                    WHERE J.job_type = 'bulkmod'
                    AND J.job_id NOT IN (SELECT B.job_id from bulkmod_job as B)
                    AND NOT J.deleted"""
        ,""" INSERT INTO chargemol_job (job_id)
                SELECT J.job_id FROM alljob AS J
                    WHERE J.job_type = 'chargemol'
                    AND J.job_id NOT IN (SELECT C.job_id from chargemol_job as C)
                    AND NOT J.deleted"""
        ,""" INSERT INTO vib_job (job_id)
                SELECT J.job_id FROM alljob AS J
                    WHERE J.job_type = 'vib'
                    AND J.job_id NOT IN (SELECT V.job_id from vib_job as V)
                    AND NOT J.deleted"""
        ,""" INSERT INTO neb_job (job_id)
                SELECT J.job_id FROM alljob AS J
                    WHERE J.job_type = 'neb'
                    AND J.job_id NOT IN (SELECT N.job_id from neb_job as N)
                    AND NOT J.deleted"""
        ,""" INSERT INTO dos_job (job_id)
                SELECT J.job_id FROM alljob AS J
                    WHERE J.job_type = 'dos'
                    AND J.job_id NOT IN (SELECT D.job_id from dos_job as D)
                    AND NOT J.deleted"""]))

populate_substructs = Rule(name = 'substructs'
    ,metatemp = PureSQL([
    """INSERT INTO molecule (struct_id)
        SELECT S.struct_id from struct AS S
        WHERE S.system_type = 'molecule'
        AND S.struct_id NOT IN (SELECT molecule.struct_id from molecule)"""
    ,"""INSERT INTO bulk (struct_id)
        SELECT S.struct_id from struct AS S
        WHERE S.system_type = 'bulk'
        AND S.struct_id NOT IN (SELECT bulk.struct_id from bulk)"""
    ,"""INSERT INTO surface (struct_id)
        SELECT S.struct_id from struct AS S
                        WHERE S.system_type = 'surface'
                        AND S.struct_id NOT IN (SELECT surface.struct_id from surface)"""]))


comp_cols = ['element_id','has_fixed'
            ,'count','count_fixed','count_norm'
            ,'frac','frac_fixed','fixed_norm']

# if any rows with a particular job have been added, we assume all have been added
populate_struct_composition = Rule(name='composition'
    ,query = """SELECT S.struct_id,S.raw
                FROM  struct AS S
                WHERE S.struct_id NOT IN (SELECT C.struct_id FROM struct_composition AS C)"""
    ,template    = SimpleTemp(load_comp,['raw'],comp_cols)
    ,metatemp    = SimpleInsert('struct_composition',['struct_id']+comp_cols)
    )

comp_strs = Rule(name='composition_strs'
    ,metatemp = PureSQL(["""
        UPDATE struct AS S SET S.composition_norm =
        (select  GROUP_CONCAT(CONCAT('[',C.element_id,',',C.count_norm,']') ORDER BY C.element_id ASC)
                FROM struct_composition as C
                WHERE C.struct_id = S.struct_id)

            ,S.composition=
              (select  GROUP_CONCAT(CONCAT('[',C.element_id,',',C.count,']') ORDER BY C.element_id ASC)
                    FROM struct_composition as C
                    WHERE C.struct_id = S.struct_id)

            ,S.metal_comp=
                (select  GROUP_CONCAT(CONCAT('[',C.element_id,',',C.count,']') ORDER BY C.element_id ASC)
                      FROM struct_composition as C
                      WHERE C.struct_id = S.struct_id
                      AND C.element_id NOT IN (1,2,6,7,8,9,10,16,17,18))
        WHERE S.struct_id > 0"""
            ]))


update_pointgroup = Rule(name='update_pointgroup'
    ,query = """SELECT M.struct_id,S.raw
                FROM molecule AS M
                    JOIN struct AS S USING (struct_id)
                WHERE M.pointgroup IS NULL"""
    ,template   = Temp(tempfuncs=[TempFunc(get_pointgroup
                                          ,name = 'pointgroup'
                                          ,args = [Arg('json_to_traj')])
                                 ,TempFunc(json_to_traj
                                          ,args = [Arg('raw')])])

    ,metatemp   = SimpleUpdate(tab  = molecule
                              ,cols = ['pointgroup']))

update_spacegroup = Rule(name='update_spacegroup'
    ,query = """SELECT S.struct_id,S.raw
                    FROM struct AS S
                WHERE S.spacegroup IS NULL"""
    ,template   = Temp(tempfuncs=[TempFunc(get_spacegroup
                                          ,name = 'spacegroup'
                                          ,args = [Arg('json_to_traj')])
                                 ,TempFunc(json_to_traj
                                          ,args = [Arg('raw')])])

    ,metatemp   = SimpleUpdate(tab  = struct
                              ,cols = ['spacegroup']))

#######################

# Calc other cols only relevant for VASP jobs
calc_other_pairs = {'prec'      : 'str'
                   ,'luse_vdw'  : 'bool'
                   ,'gga'       : 'bool'
                   ,'lvhar'     : 'bool'
                   ,'zab_vdw'   : 'float'
                   ,'algo'      : 'str'
                   ,'nelmdl'    : 'int'
                   ,'ibrion'    : 'int'
                   ,'lreal'     : 'str'
                   }

# Calc other cols only relevant for VASP
vasp_key_tempfuncs = [TempFunc(get_vasp_key
         ,name = x
         ,args = noIndex(['dftcode','log','key '+x,'cast '+y]))
                            for x,y in calc_other_pairs.items()]

# Calc other cols relevant for all three codes
dftdep_tempfuncs = [TempFunc(dftcode_dependent
                            ,name = x
                            ,args = noIndex(['dftcode'
                                            ,'log'
                                            ,'get_%s_gpaw'%x
                                            ,'get_%s_qe'%x
                                            ,'get_%s_vasp'%x
                                            ,'identity'
                                            ,'identity'])) for x in other_cols if x not in ['nbands','maxstep','kpts','gamma']]
# Calc other cols relevant for all three codes that depend on files other than log
dftdep_dict_tempfuncs = [TempFunc(dftcode_dependent
                                 ,name = x
                                 ,args = noIndex(['dftcode'
                                                  ,'files'
                                                  ,'get_%s_gpaw'%x
                                                  ,'get_%s_qe'%x
                                                  ,'get_%s_vasp'%x
                                                  ,'identity'
                                                  ,'identity'])) for x in  ['maxstep','kpts','gamma']]
# Calc other cols that can 'only' be scraped from params.json
get_pairs = {'fmax'              :'float'
            ,'strain'            :'float'
            ,'energy_cut_off'    :'float'
            ,'bonded_inds'       :'str'
            ,'step_size'         :'float'
            ,'spring'            :'float'
            ,'delta'             :'float'
            }

get_tempfuncs = [TempFunc(get
                         ,name = x
                         ,args = noIndex(['paramdict','key '+x,'cast '+y])) for x,y in get_pairs.items()]

qe_tempfuncs = [TempFunc(x,x.__name__[4:],args = noIndex(['pwinp','dftcode']))
                    for x in [get_cell_factor,get_cell_dofree]]

# All calc_other column names
calc_other_cols = (list(calc_other_pairs.keys())
                 + list (get_pairs.keys())
                 + [o for o in other_cols if o != 'kpts']
                 + ['kx','ky','kz','cell_dofree','cell_factor'])

calc_other_args = noIndex(calc_other_cols)
double_co_args  = [val for val in calc_other_args for _ in (0, 1)]



# Main rule
populate_calc_other = Rule(name='calc_other'
    ,query    = """SELECT R.job_id,J.log,J.pwinp,J.kptcar,J.paramdict,C.dftcode
                     FROM relax_job AS R
                     JOIN alljob AS J USING (job_id)
                     JOIN calc AS C  USING (calc_id)
                     WHERE R.calc_other_id IS NULL"""
    ,template = Temp(constants = merge_dicts([{'key ' +x:Const(x) for x in calc_other_pairs.keys()} # type: ignore
                                             ,{'cast '+y:Const(y) for y in calc_other_pairs.values()}
                                             ,{'key ' +x:Const(x) for x in get_pairs.keys()}
                                             ,{'cast '+y:Const(y) for y in get_pairs.values()}
                                             ,{'identity' : Const(identity)}
                                             ]+[{x.__name__ : Const(x)} for x in get_fns])

                    ,tempfuncs = [TempFunc(identity,'kx',args=[Arg('kpts',0)])
                                 ,TempFunc(identity,'ky',args=[Arg('kpts',1)])
                                 ,TempFunc(identity,'kz',args=[Arg('kpts',2)])
                                 ,TempFunc(get_dw,'dw',args=noIndex(['dftcode','log']))
                                 ,TempFunc(get_mixtype,'mixtype',args=noIndex(['dftcode','log']))
                                 ,TempFunc(pair,args=noIndex(['log','paramdict']))
                                 ,TempFunc(triple,'files',args=noIndex(['log','pwinp','kptcar']))
                                 ,TempFunc(dftcode_dependent
                                           ,name = 'nbands'
                                          ,args = noIndex(['dftcode'
                                                          ,'pair' # THIS IS WHAT IS DIFFERENT
                                                          ,'get_nbands_gpaw'
                                                          ,'get_nbands_qe'
                                                          ,'get_nbands_vasp'
                                                          ,'identity'
                                                          ,'identity']))]
                                 + dftdep_tempfuncs
                                 + dftdep_dict_tempfuncs
                                 + vasp_key_tempfuncs
                                 + get_tempfuncs
                                 + qe_tempfuncs
                    )
    ,metatemp = MetaTemp([Block(name = 'insert_calc'
                               ,text = """INSERT  into calc_other ({0})
                                         SELECT {1} FROM DUAL
                                        WHERE NOT EXISTS (SELECT (1) FROM calc_other WHERE {2})
                                        """.format(','.join(calc_other_cols)
                                                  ,','.join(['%s']*len(calc_other_cols))
                                                  ,' AND '.join(['({0}=%s OR ({0} IS NULL AND %s IS NULL ))'.format(x) for x in calc_other_cols]))
                                ,args = calc_other_args+double_co_args)
                        ,Block(name = 'get_calc'
                              ,text = """SELECT calc_other_id FROM calc_other WHERE {0}
                                        """.format(' AND '.join(['({0}=%s OR ({0} IS NULL AND %s IS NULL ))'.format(x) for x in calc_other_cols]))
                              ,args = double_co_args)
                        , Block(name = 'update'
                               ,text = "UPDATE relax_job SET calc_other_id = %s WHERE job_id=%s"
                               ,args = [Arg('get_calc',0),Arg('job_id')])]))

kden_cols = ['kptden_x','kptden_y','kptden_z']

kptden = Rule(name='kptden'
    ,query = """SELECT T.job_id,T.traj_id,O.kx,O.ky,O.kz%s
                FROM traj AS T
                    JOIN struct    AS S USING (struct_id)
                    JOIN cell        AS C USING (cell_id)
                    JOIN relax_job AS J USING (job_id)
                    JOIN calc_other AS O USING (calc_other_id)
                WHERE T.kptden_x IS null
            """%(''.join([',C.%s'%c for c in cell_cols]))
    ,template = SimpleTemp(get_kptden
                          ,['kx','ky','kz']+cell_cols
                          ,kden_cols)
    ,metatemp=SimpleUpdate(traj,kden_cols))


populate_struct_maps = Rule(name='struct_maps'
    ,metatemp=PureSQL(["""
    INSERT INTO chargemol_map (job_id,charge_id)

    SELECT
        F.job_id,CJ.job_id
    FROM
        chargemol_job AS CJ
            JOIN struct AS CS USING (struct_id)
            JOIN cell AS CC USING (cell_id)
            JOIN similar_struct AS SS USING (struct_id) -- pairs of structures with same sym, chemical symbols, and constrained atoms (all non-float data)
            JOIN finaltraj AS F ON F.struct_id = SS.struct_id2
            JOIN struct    AS S ON F.struct_id = S.struct_id
            JOIN cell      AS C ON C.cell_id = S.cell_id
    WHERE
        ABS(CC.a0 - C.a0) < 0.01
            AND ABS(CC.a1 - C.a1) < 0.01
            AND ABS(CC.a2 - C.a2) < 0.01
            AND ABS(CC.b0 - C.b0) < 0.01
            AND ABS(CC.b1 - C.b1) < 0.01
            AND ABS(CC.b2 - C.b2) < 0.01
            AND ABS(CC.c0 - C.c0) < 0.01
            AND ABS(CC.c1 - C.c1) < 0.01
            AND ABS(CC.c2 - C.c2) < 0.01
            AND NOT EXISTS( SELECT (1)
                FROM  atom AS A JOIN atom AS CA
                WHERE   A.struct_id = S.struct_id
                    AND CA.struct_id = CS.struct_id
                    AND A.atom_id = CA.atom_id
                    AND (  ABS(A.x - CA.x) > 0.01
                        OR ABS(A.y - CA.y) > 0.01
                        OR ABS(A.z - CA.z) > 0.01))

        ON DUPLICATE KEY UPDATE job_id=F.job_id"""])) # could replace 'chargemol' with 'vib' and reuse code


struct_strs = Rule('struct_strs'
    ,metatemp=PureSQL(["""
         UPDATE struct AS S SET S.str_symbols =
            (SELECT GROUP_CONCAT(A.element_id)
                FROM atom as A WHERE A.struct_id = S.struct_id)
  ,S.str_constraints =
    (SELECT GROUP_CONCAT(A.constrained)
        FROM atom as A WHERE A.struct_id = S.struct_id)

,S.symmetry = COALESCE((SELECT S.spacegroup
                FROM bulk AS B
                WHERE B.struct_id=S.struct_id)
            ,(SELECT M.pointgroup
                FROM molecule AS M
                WHERE M.struct_id=S.struct_id)
            ,'1')

    WHERE S.struct_id > 0            """]))

pop_similar_struct = Rule('pop_similar_struct'
    ,metatemp = PureSQL(["""INSERT INTO similar_struct  (struct_id,struct_id2)
                        SELECT S.struct_id,T.struct_id
                        FROM struct AS S JOIN struct AS T
                        WHERE S.str_symbols = T.str_symbols
                        AND S.str_constraints=T.str_constraints
                        AND S.symmetry = T.symmetry
                        ON DUPLICATE KEY UPDATE similar_struct.struct_id=similar_struct.struct_id"""]))

update_vacuum = Rule('update_vacuum'
    ,query = """SELECT U.struct_id,S.raw
                    FROM struct AS S JOIN surface AS U USING (struct_id)
                WHERE U.vacuum IS NULL"""
    ,template   = Temp(tempfuncs=[TempFunc(get_vacuum
                                          ,name = 'vacuum'
                                          ,args = [Arg('json_to_traj')])
                                 ,TempFunc(json_to_traj
                                          ,args = [Arg('raw')])])
    ,metatemp   = SimpleUpdate(tab  = surface
                              ,cols = ['vacuum']))

update_layer = Rule('update_layer'
    ,query = """SELECT U.struct_id,S.geo_graph
                FROM struct AS S
                JOIN surface AS U USING (struct_id)
                JOIN atom AS A USING (struct_id)
                GROUP BY U.struct_id
            HAVING SUM(A.layer is null)!=0"""
    ,template=Temp(tempfuncs=[TempFunc(json_to_graph
                                      ,args=[Arg('geo_graph')])
                            ,TempFunc(layers
                                    ,args=[Arg('json_to_graph')])
                            ,TempFunc(identity
                                    ,name='layer'
                                    ,args=[Arg('layers',1)])
                            ,TempFunc(identity
                                    ,name='atom_id'
                                    ,args=[Arg('layers',0)])])
    ,metatemp=SimpleUpdate(atom,['layer']))


pop_kpts = Rule('pop_kpts'
    ,metatemp=PureSQL(["""UPDATE calc_other AS C
                        SET  kpts = CONCAT('[', C.kx, ',', C.ky, ',', C.kz, ']')
                        WHERE C.calc_other_id > 0"""]))
rules = [geograph
             ,elemental
             ,voronoi
             ,populate_subjobs
             ,populate_substructs
             ,populate_struct_composition
             ,comp_strs
             ,update_pointgroup
             ,update_spacegroup
             ,update_vacuum
             ,populate_calc_other
             ,kptden
             ,populate_struct_maps
             ,struct_strs
             ,pop_similar_struct
             ,update_layer
             ,pop_kpts]
