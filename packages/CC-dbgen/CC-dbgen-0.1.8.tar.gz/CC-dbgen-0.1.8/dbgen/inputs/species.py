# External
import os
# Internal
from dbgen.support.datatypes.table     import Table,Col,FK
from dbgen.support.datatypes.rule import Rule
from dbgen.support.datatypes.temp      import Temp,TempFunc
from dbgen.support.datatypes.misc      import Arg
from dbgen.support.utils               import mkInsCmd,mkUpdateCmd
from dbgen.support.datatypes.metatemp  import MetaTemp,Block,SimpleUpdate,PureSQL
from dbgen.support.datatypes.sqltypes  import Varchar
from dbgen.inputs.extra                import surface

from dbgen.scripts.Pure.Atoms.get_bulk           import get_bulk
from dbgen.scripts.Pure.Atoms.get_miller         import get_miller
from dbgen.scripts.Pure.Atoms.surface_bulkstruct import surface_bulkstruct
from dbgen.scripts.Pure.Atoms.get_pure_struct    import get_pure_struct
from dbgen.scripts.Pure.Atoms.json_to_traj       import json_to_traj
from dbgen.scripts.Pure.Atoms.get_miller         import get_miller
from dbgen.scripts.Pure.Misc.pmg_to_ase          import pmg_to_ase
################################################################
################################################################
pypth = os.path.dirname(__file__)

functions = {
     'get_bulk'             : pypth + "Pure/Atoms/get_bulk.py"
    ,'get_miller'           : pypth + "Pure/Atoms/get_miller.py"
    ,'surface_bulkstruct'   : pypth + "Pure/Atoms/surface_bulkstruct.py"
    ,'get_pure_struct'      : pypth + "Pure/Atoms/get_pure_struct.py"
    ,'json_to_traj'         : pypth + "Pure/Atoms/json_to_traj.py"
    ,'pmg_to_ase'           : pypth + "Pure/Misc/pmg_to_ase.py"}
################################################################
################################################################
################################################################

species = Table('species'
    ,desc="""A combination of composition and structural information (no floats)"""
    ,cols=[Col('species_id',               pk   = True, auto = True)
          ,Col('name',          Varchar(), uniq = True)
          ,Col('nickname',      Varchar())
          ,Col('composition',   Varchar())])

bulkspecies = Table('bulkspecies'
    ,desc = 'Properties of species that are bulks'
    ,cols = [Col('species_id',    pk=True)
            ,Col('pure_struct_id',nn=True)]
    ,fks  = [FK('species_id',    'species')
            ,FK('pure_struct_id','pure_struct')])

molspecies = Table('molspecies'
    ,desc = 'Properties of species that are molecules. IN THE FUTURE, the SMILES string should be here because pointgroup + composition is underspecified'
    ,cols = [Col('species_id',pk = True)
            ,Col('pointgroup',nn = True)]
    ,fks  = [FK('species_id','species')
             ,FK('pure_struct_id','pure_struct')])

surfspecies = Table('surfspecies'
    ,desc = 'How should this be specified ??? And 2D materials?'
    ,cols = [Col('species_id',                  pk = True)
            ,Col('pure_struct_id',              nn = True)
            ,Col('facet',           Varchar(),  nn = True)]
    ,fks  = [FK('species_id','species')
            ,FK('pure_struct_id','pure_struct')])

species_composition = Table('species_composition'
    ,desc='Mapping table between species and element'
    ,cols = [Col('species_id',pk = True)
            ,Col('element_id',pk = True)
            ,Col('count',     nn = True)]
    ,fks  = [FK('species_id','species')
            ,FK('element_id','element')])

########################################################

pure_struct = Table('pure_struct'
    ,desc = 'Structure abstraction developed by Ankit Jain'
    ,cols = [Col('pure_struct_id',              pk = True,auto = True)
            ,Col('name',            Varchar(),  nn = True,uniq = True)
            ,Col('spacegroup')
            ,Col('free')
            ,Col('nickname',        Varchar())
            ])

tables = [species
         ,bulkspecies
         ,molspecies
         ,surfspecies
         ,species_composition
         ,pure_struct]

################################################################
################################################################
################################################################
nick_dict = {'AB_1_a_b_225'     : 'rocksalt'
            ,'AB_1_a_c_216'     : 'zincblende'
            ,'AB_1_a_b_221'     : 'cesium chloride'
            ,'A_1_a_225'        : 'fcc'
            ,'A_1_a_229'        : 'bcc'
            ,'A_2_c_194'        : 'hcp'
            ,'A_2_a_227'        : 'diamond'
            ,'AB3_1_a_d_221'    : 'anti-ReO3'
            ,'A2B3_8_ad_e_206'  : 'antibixbyite'
            # add rutile/perovskite
            }

pop_nickname = Rule('pop_nickname'
    ,metatemp=PureSQL(["""UPDATE pure_struct
                        SET   nickname = '{0}'
                        WHERE name     = '{1}'
                        AND pure_struct_id > 0
                        """.format(v,k) for k,v in nick_dict.items()]))

pop_compstr = Rule('species_compstr'
    ,metatemp=PureSQL([""" UPDATE species AS S SET S.composition=
                  (select  GROUP_CONCAT(CONCAT('[',C.element_id,',',C.count,']') ORDER BY C.element_id ASC)
                        FROM species_composition as C
                        WHERE C.species_id = S.species_id)"""]))

update_species_fk = Rule('species_fk'
    ,metatemp= PureSQL(["""UPDATE struct AS S SET S.species_id = (
                SELECT  P.species_id FROM species AS P
                LEFT JOIN bulkspecies B USING (species_id)
                LEFT JOIN molspecies M USING (species_id)
                WHERE S.composition_norm = P.composition
                 AND    (S.system_type = 'bulk'
                        AND B.pure_struct_id = S.pure_struct_id)
                        OR (S.system_type = 'molecule'
                        AND M.pointgroup = S.symmetry))
                WHERE S.struct_id > 0"""]))

pop_pure = Rule('pop_pure_struct'
    ,query    = 'SELECT S.struct_id,S.raw FROM struct AS S WHERE pure_struct_id IS NULL'
    ,template = Temp(tempfuncs=[TempFunc(get_bulk
                                        ,args=[Arg('json_to_traj')])
                                ,TempFunc(json_to_traj
                                        ,args=[Arg('raw')])
                                ,TempFunc(get_pure_struct
                                        ,args=[Arg('get_bulk')])])
    ,metatemp=MetaTemp([Block(name = 'insert'
                             ,text = mkInsCmd('pure_struct',['name','spacegroup','free'],sqlite=False)
                             ,args = [Arg('get_pure_struct',i) for i in range(3)])
                        ,Block(name='query'
                            ,text="""SELECT pure_struct_id FROM pure_struct WHERE name=%s"""
                            ,args=[Arg('get_pure_struct',0)])
                        ,Block(name='insert_fk'
                                ,text=mkUpdateCmd('struct',['pure_struct_id'],['struct_id'])
                                ,args=[Arg('query',0),Arg('struct_id')])]))

underlying = Rule('underlying'
    ,query    = """SELECT U.struct_id,S.raw
                    FROM struct AS S
                    JOIN surface AS U USING (struct_id)
                    WHERE U.facet_h IS NULL"""
    ,template = Temp(tempfuncs = [TempFunc(json_to_traj
                                          ,args = [Arg('raw')])
                                 ,TempFunc(surface_bulkstruct
                                          ,args = [Arg('json_to_traj')])
                                 ,TempFunc(pmg_to_ase
                                         ,args=[Arg('surface_bulkstruct')])
                                 ,TempFunc(get_bulk
                                          ,args=[Arg('pmg_to_ase')])
                                 ,TempFunc(get_miller
                                          ,args=[Arg('surface_bulkstruct')])
                                 ,TempFunc(get_pure_struct
                                          ,args=[Arg('get_bulk')])])
    ,metatemp = MetaTemp([Block(name = 'insert'
                             ,text = mkInsCmd('pure_struct',['name','spacegroup','free'],sqlite=False)
                             ,args = [Arg('get_pure_struct',i) for i in range(3)])
                        ,Block(name='query'
                            ,text="""SELECT pure_struct_id FROM pure_struct WHERE name=%s"""
                            ,args=[Arg('get_pure_struct',0)])
                        ,Block(name='insert_fk'
                                ,text=mkUpdateCmd('surface',['pure_struct_id'],['struct_id'])
                                ,args=[Arg('query',0),Arg('struct_id')])
                        ,Block(name='update_miller'
                              ,text = mkUpdateCmd('surface',['facet_h','facet_k','facet_l'],['struct_id'])
                              ,args = [Arg('get_miller',i) for i in range(3)]
                                     +[Arg('struct_id')])]))

rules = [pop_pure
             ,underlying
             ,pop_nickname
             ,pop_compstr
             ,update_species_fk]
