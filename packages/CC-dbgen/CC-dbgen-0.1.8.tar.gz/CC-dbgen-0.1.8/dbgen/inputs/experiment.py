import os
from dbgen.support.datatypes.rule import Rule
from dbgen.support.datatypes.temp      import SimpleTemp,Const
from dbgen.support.datatypes.metatemp  import SimpleInsert,MetaTemp,Block,noIndex
from dbgen.support.datatypes.misc      import Arg
from dbgen.support.datatypes.sqltypes  import Varchar,Decimal

from dbgen.support.utils               import mkInsCmd
from dbgen.support.datatypes.table      import Table,Col,FK
from dbgen.scripts.IO.parse_keld import parse_keld
pypth = os.path.dirname(__file__)

##########################################################################################
keld_table = Table('keld_solids'
    ,desc='Data from Keld L. with experimental properties for bulk materials'
    ,cols = [Col('id',                            pk=True,auto=True)
            ,Col('name',             Varchar(),       nn=True)
            ,Col('job_name',         Varchar(),       nn=True)
            ,Col('lattice_parameter',Decimal())
            ,Col('cohesive_energy',  Decimal())
            ,Col('bulkmod',          Decimal())
            ,Col('structure',        Varchar())
            ,Col('magmom',           Decimal())])

tables = [keld_table]

##########################################################################################
##########################################################################################
##########################################################################################

keld_cols2 = ['name_short','pure_struct_id','spacegroups'
             ,'name_mid','element_id','count'
             ,'name_long','property','value']

s_d_cols = ['struct_dataset_id','species_id','property','value']

pop_keld = Rule('keld'
    ,template = SimpleTemp(parse_keld,[],keld_cols2
                          ,{'k':Const('keld_solids')})
    ,metatemp = MetaTemp([
         Block(name = 'insert_species'
              ,text = mkInsCmd('species',['name','nickname'])
              ,args = noIndex(['name_short','name_short']))

        ,Block(name = 'insert_pure_struct'
              ,text = mkInsCmd('pure_struct',['name','spacegroup'])
              ,args = noIndex(['pure_struct_id','spacegroups']))

        ,Block(name = 'query_species_short'
              ,text = 'SELECT species_id FROM species WHERE name=%s'
              ,args = [Arg('name_short')])

        ,Block(name = 'query_pure_struct'
              ,text = 'SELECT pure_struct_id FROM pure_struct WHERE name=%s'
              ,args = [Arg('pure_struct_id')])

        ,Block(name = 'insert_bulk_species'
              ,text = mkInsCmd('bulkspecies',['species_id','pure_struct_id'],sqlite=False)
              ,args = [Arg('query_species_short')
                      ,Arg('query_pure_struct')])

        ,Block(name = 'query_species_mid'
              ,text = 'SELECT species_id FROM species WHERE name=%s'
              ,args = [Arg('name_mid')])

        ,Block(name = 'insert_species_comp'
              ,text = mkInsCmd('species_composition',['species_id','element_id','count'],sqlite=False)
              ,args = [Arg('query_species_mid')
                      ,Arg('element_id')
                      ,Arg('count')])

        ,Block(name = 'query_species_long'
              ,text = 'SELECT species_id FROM species WHERE name=%s'
              ,args = [Arg('name_long')])

        ,Block(name = 'insert_dataset'
              ,text = """INSERT INTO struct_dataset (name) VALUES (%s)
                      ON DUPLICATE KEY UPDATE struct_dataset_id=struct_dataset_id"""
              ,args = [Arg('k')])

        ,Block(name = 'query_dataset'
              ,text = """SELECT  struct_dataset_id FROM struct_dataset
                        WHERE name = %s"""
              ,args = [Arg('k')])

        ,Block(name = 'insert_dataset_elem'
              ,text = mkInsCmd('struct_dataset_element',s_d_cols,sqlite=False)
              ,args = [Arg('query_dataset')
                      ,Arg('query_species_long')
                      ,Arg('property'),Arg('value')])]))

rules = [pop_keld]
