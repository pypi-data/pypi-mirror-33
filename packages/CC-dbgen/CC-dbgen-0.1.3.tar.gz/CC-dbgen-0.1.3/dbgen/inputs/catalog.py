# External Modules
from os import environ
# Internal Modules
from dbgen.inputs.species              import nick_dict
from dbgen.core.lists                  import merge_dicts
from dbgen.support.datatypes.rule      import Rule
from dbgen.support.datatypes.temp      import Temp,TempFunc,Const
from dbgen.support.datatypes.misc      import Arg,noIndex
from dbgen.support.datatypes.metatemp  import MetaTemp,Block,SimpleUpdate
from dbgen.support.utils               import mkInsCmd,mkUpdateCmd
from dbgen.inputs.basics               import alljob

from dbgen.scripts.Pure.Misc.get                import get
from dbgen.scripts.Pure.Misc.get_               import get_
from dbgen.scripts.Pure.Load.get_catalog_ads    import get_catalog_ads
from dbgen.scripts.Pure.Load.get_catalog_facet  import get_catalog_facet
"""
Anything that seems Catalog-specific (absolutely useless for jobs generated
elsewhere) should go here
"""
################################################################################
pypth = environ['DBGEN_ROOT']+'/scripts/'

functions  = {
    'get'                : pypth+"Pure/Misc/get.py"
    ,'get_'              : pypth+"Pure/Misc/get_.py"
    ,'get_catalog_facet' : pypth+"Pure/Load/get_catalog_facet.py"
    ,'get_catalog_ads'   : pypth+"Pure/Load/get_catalog_ads.py"
    }
################################################################################

# Mapping from informal structure names given by user to specific pure_struct's
struct_dict = merge_dicts([{v:k,v+'_unit':k,v+'-unit':k} for k,v in nick_dict.items()])
# Additional cases
struct_dict['2DMaterial'] = 'N/A'
struct_dict['hexagonal'] = struct_dict['hcp']

pop_bulk_struct_catalog = Rule('pop_bulk_struct_catalog'
    ,query = """SELECT B.struct_id,J.paramdict
                FROM bulk AS B
                JOIN struct AS S USING (struct_id)
                JOIN traj USING (struct_id)
                JOIN alljob AS J USING (job_id)
                WHERE J.paramdict != ''
                AND S.pure_struct_id_catalog IS NULL
                AND NOT J.deleted"""
    ,template = Temp(constants={'struct_dict'   : Const(struct_dict)
                               ,'structure_key' : Const('structure')
                               ,'str'           : Const('str')
                               ,'unknown'       : Const('unknown')}
                  ,tempfuncs=[TempFunc(get
                                      ,name='nickname'
                                      ,args=noIndex(['paramdict'
                                                    ,'structure_key'
                                                    ,'str']))
                             ,TempFunc(get_
                                      ,'pure_struct_name'
                                      ,args=noIndex(['struct_dict'
                                                    ,'nickname'
                                                    ,'unknown']))])
    ,metatemp = MetaTemp([Block('insert_pure_struct'
                               ,mkInsCmd('pure_struct',['name'])
                               ,args=[Arg('pure_struct_name')])
                         ,Block('query_pure_struct'
                             ,"""SELECT pure_struct_id FROM pure_struct WHERE name=%s"""
                             ,args=[Arg('pure_struct_name')])
                        ,Block('update_fk'
                             ,mkUpdateCmd('struct',['pure_struct_id_catalog'],['struct_id'])
                             ,args=noIndex(['query_pure_struct','struct_id']))]))

pop_surf_struct_catalog = Rule('pop_surf_struct_catalog'
    ,query="""SELECT S.struct_id,J.paramdict
                FROM surface AS S
                JOIN traj USING (struct_id)
                JOIN alljob AS J USING (job_id)
                WHERE J.paramdict != ''
                AND S.facet_l_catalog IS NULL
                AND NOT J.deleted """
    ,template=Temp(constants={'struct_dict'     : Const(struct_dict)
                             ,'structure_key'   : Const('structure')
                             ,'str'             : Const('str')
                             ,'unknown'         : Const('unknown')}
                  ,tempfuncs=[TempFunc(get
                                      ,name='nickname'
                                      ,args=noIndex(['paramdict'
                                                    ,'structure_key'
                                                    ,'str']))

                             ,TempFunc(get_catalog_facet
                                     ,args=[Arg('paramdict')])

                             ,TempFunc(get_
                                      ,'pure_struct_name'
                                      ,args=noIndex(['struct_dict'
                                                    ,'nickname'
                                                    ,'unknown']))])
    ,metatemp = MetaTemp([Block('insert_pure_struct'
                             ,mkInsCmd('pure_struct',['name'])
                             ,args=[Arg('pure_struct_name')])
                       ,Block('query_pure_struct'
                             ,"""SELECT pure_struct_id FROM pure_struct WHERE name=%s"""
                             ,args=[Arg('pure_struct_name')])
                       ,Block('update_fk'
                             ,mkUpdateCmd('surface'
                                         ,['pure_struct_id_catalog'
                                          ,'facet_h_catalog'
                                          ,'facet_k_catalog'
                                          ,'facet_l_catalog']
                                         ,['struct_id'])
                             ,args=[Arg('query_pure_struct')
                                    ,Arg('get_catalog_facet',0)
                                    ,Arg('get_catalog_facet',1)
                                    ,Arg('get_catalog_facet',2)
                                    ,Arg('struct_id')])]))

pop_ads_catalog = Rule('pop_ads_catalog'
    ,query = """SELECT J.job_id,S.struct_id,J.paramdict
                FROM surface AS S
                JOIN traj USING (struct_id)
                JOIN alljob AS J USING (job_id)
                WHERE J.paramdict like '%%adsorbates%%'
                AND J.ads_catalog IS NULL
                AND NOT J.deleted"""
    ,template=Temp(constants={'ads': Const('adsorbates')
                             ,'str': Const('str')}
        ,tempfuncs=[TempFunc(get
                            ,name='ads_json'
                            ,args=noIndex(['paramdict'
                                            ,'ads'
                                            ,'str']))
                   ,TempFunc(get_catalog_ads
                            ,args=[Arg('ads_json')])])
    ,metatemp=MetaTemp([Block('insert'
                            ,mkUpdateCmd('atom',['struct_adsorbate_id_catalog'],['struct_id','atom_id'])
                            ,args=[Arg('get_catalog_ads',0)
                                  ,Arg('struct_id')
                                  ,Arg('get_catalog_ads',1)])
                    ,Block('insert2'
                        ,mkUpdateCmd('alljob',['ads_catalog'],['job_id'])
                        ,args=noIndex(['ads_json','job_id']))]))

pop_struct_catalog = Rule('pop_struct_catalog'
    ,query = """SELECT J.job_id,J.paramdict
                FROM alljob AS J
                WHERE J.paramdict like '%%structure%%'
                AND J.structure_catalog IS NULL
                AND NOT J.deleted """
    ,template=Temp(constants={'struct': Const('structure')
                             ,'str'   : Const('str')}
        ,tempfuncs=[TempFunc(get
                            ,name = 'structure_catalog'
                            ,args = noIndex(['paramdict'
                                            ,'struct'
                                            ,'str']))])
    ,metatemp = SimpleUpdate(alljob,['structure_catalog']))

rules = [pop_bulk_struct_catalog
             ,pop_surf_struct_catalog
             ,pop_ads_catalog
             ,pop_struct_catalog]
