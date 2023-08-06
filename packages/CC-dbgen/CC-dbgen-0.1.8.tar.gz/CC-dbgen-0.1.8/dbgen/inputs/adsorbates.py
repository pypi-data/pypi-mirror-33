import os
from dbgen.support.datatypes.table     import Table,Col,FK
from dbgen.support.datatypes.table     import Table,Col,FK,View
from dbgen.support.datatypes.temp      import Temp,TempFunc,SimpleTemp
from dbgen.support.datatypes.misc      import Arg,noIndex
from dbgen.support.datatypes.metatemp  import PureSQL,MetaTemp,Block
from dbgen.support.datatypes.rule      import Rule
from dbgen.support.datatypes.sqltypes  import Varchar,Decimal

from dbgen.support.utils               import mkInsCmd
from dbgen.core.lists                  import flatten

from dbgen.scripts.Pure.Graph.json_to_graph  import json_to_graph
from dbgen.scripts.Pure.Graph.identify_ads   import identify_ads
##########################################################################################
##########################################################################################
##########################################################################################
# Constants
###########
pypth = os.path.dirname(__file__)
cell_cols = ['a0','a1','a2','b0','b1','b2','c0','c1','c2']

ads = {'H':{1:1},'N':{7:1},'O':{8:1},'C':{6:1},'NH':{1:1,7:1},'OH':{8:1,1:1}
      ,'CH':{1:1,6:1},'NH2':{1:2,7:1},'H2O':{1:2,8:1},'CH2':{1:2,6:1}
      ,'NH3':{1:3,7:1},'CH3':{1:3,6:1},'N2':{7:2},'NNH':{1:1,7:2},'NNH2':{1:2,7:2}
      ,'NNH3':{1:3,7:2},'H2':{1:2},'C2':{6:2},'N2':{7:2},'O2':{8:2}
      ,'OOH':{1:1,8:2},'CHO':{1:1,6:1,8:1},'COOH':{1:1,6:1,8:2}
      ,'CO':{6:1,8:1},'OCCO':{6:2,8:2},'OCCHO':{1:1,6:2,8:2}
      }
##########################################################################################
##########################################################################################
##########################################################################################

functions = {
     'json_to_graph'    : pypth+'Pure/Graph/json_to_graph.py'
    ,'identify_ads'        : pypth+'Pure/Graph/identify_ads.py'

} # type: dict

##########################################################################################
##########################################################################################
##########################################################################################

adsorbate = Table('adsorbate'
    ,desc = 'Species that can adsorb onto a surface'
    ,cols = [Col('adsorbate_id',            pk = True, auto = True)
            ,Col('name',        Varchar(),  nn = True, uniq = True)
            ,Col('composition', Varchar())])

adsorbate_composition = Table('adsorbate_composition'
    ,'Components of an adsorbate'
    ,cols = [Col('adsorbate_id',  pk = True)
            ,Col('element_id',    pk = True)
            ,Col('number',        nn = True)])

struct_adsorbate = Table('struct_adsorbate'
    ,'An adsorbate considered on a particular surface'
    ,cols = [Col('struct_id',                   pk=True)
            ,Col('adsorbate_id',                pk=True)
            ,Col('struct_adsorbate_id',         pk=True)
            ,Col('site',                Varchar())]
    ,fks = [FK('struct_id',   'struct')
           ,FK('adsorbate_id','adsorbate')])

tables = [adsorbate
         ,adsorbate_composition
         ,struct_adsorbate]

##########################################################################################
##########################################################################################
##########################################################################################

ads_eng_view = View("ads_eng","""
SELECT R.ref_scheme_id                   -- SPECIFY *1* OF THESE
      ,A.adsorbate_id                    -- JOIN ON THIS
      ,J.calc_id                         -- JOIN ON THIS
      ,R.element_id                      -- SUM (number*avg_energy) WHEN GROUPING BY THIS
      ,R.component_id                    -- AVG energy IN SUBSELECT WHILE GROUPING BY THIS + Element&Component
      ,A.name                            -- human readable info
      ,E.symbol AS element               -- human readable info
      ,CE.symbol AS component            -- human readable info
      ,RS.struct_id                      -- join with struct for info to be used in constraints (e.g. kpt related things depending on bulk/molecule/surface)
      ,F.job_id                          -- join with JOB to be used in constraints (e.g. timestamp constraint to get repeatable results)
      ,F.energy/C.count AS energy_norm   -- contains fundamental information we want (averaged for each component element and summed to get adsorbate reference energy)
      ,J.calc_other_id                   -- join with calc other to filter down possible contributions to adsorbate energy
      ,AC.number                         -- how many of ELEMENT are in the adsorbate
      ,R.coef                            -- how much of each COMPONENT refjob goes into the calculation of the energy per ELEMENT atom
    FROM adsorbate_composition AS AC
    JOIN ref_scheme_reqs AS R ON AC.element_id = R.element_id
    JOIN adsorbate AS A USING (adsorbate_id)
    JOIN ref_scheme_refstruct AS RS ON RS.element_id=R.component_id AND RS.ref_scheme_id = R.ref_scheme_id
    JOIN finaltraj AS F ON F.struct_id = RS.struct_id
    JOIN relax_job AS J ON J.job_id = F.job_id
    JOIN element AS E ON E.element_id=R.component_id
    JOIN element AS CE ON CE.element_id=R.component_id
    JOIN struct_composition AS C ON C.element_id=RS.element_id AND C.struct_id = F.struct_id""")
views = [ads_eng_view]
##########################################################################################
##########################################################################################
##########################################################################################


adscompstr  = "((SELECT adsorbate_id FROM adsorbate WHERE name='%s'),%d,%d)"
adscompstrs = flatten([[adscompstr%(k,k2,v2) for k2,v2 in v.items()] for k,v in ads.items()])
populate_adsorbate = Rule('populate_adsorbate'
    ,metatemp = PureSQL(["""INSERT INTO adsorbate (name) VALUES %s
                            ON DUPLICATE KEY UPDATE name=name"""%','.join(["('%s')"%x for x in ads.keys()])
                       ,"""INSERT INTO adsorbate_composition (adsorbate_id,element_id,number) VALUES %s
                           ON DUPLICATE KEY UPDATE adsorbate_id=adsorbate_id"""%','.join(adscompstrs)]))


#####
struct_ads_cols = ['struct_id','adsorbate_id','struct_adsorbate_id','site']
pop_struct_ads = Rule('pop_struct_ads'
    ,query = """SELECT S.struct_id,S.geo_graph
                FROM struct AS S JOIN surface USING (struct_id)
                WHERE EXISTS (SELECT A.struct_adsorbate_id IS NULL
                                AND A.element_id IN (1,6,7,8)
                              FROM atom AS A
                              WHERE A.struct_id = S.struct_id)"""

    ,template = Temp(tempfuncs = [TempFunc(json_to_graph
                                          ,args=[Arg('geo_graph')])
                                 ,TempFunc(identify_ads
                                           ,name = 'ads'
                                           ,args = [Arg('json_to_graph')])])
    ,metatemp = MetaTemp([
                     Block(name = 'adsorbate_id'
                          ,text = 'SELECT A.adsorbate_id FROM adsorbate AS A WHERE A.name=%s'
                          ,args = [Arg('ads',4)])
                    ,Block(name='adsorbate_id_many'
                          ,text ='SELECT A.adsorbate_id FROM adsorbate AS A WHERE A.name=%s'
                          ,args = [Arg('ads',2)])
                    ,Block(name = 'insert_struct_ads'
                          ,text = mkInsCmd('struct_adsorbate',struct_ads_cols,sqlite=False)
                          ,args = [Arg('struct_id')
                                  ,Arg('adsorbate_id')
                                  ,Arg('ads',3)
                                  ,Arg('ads',5)])
                    ,Block(name = 'update_atom_fk'
                          ,text = """UPDATE atom SET struct_id=%s,adsorbate_id=%s,struct_adsorbate_id=%s
                                     WHERE struct_id=%s AND atom_id=%s"""
                          ,args = [Arg('struct_id') # needed because it's a composite foreign key?
                                  ,Arg('adsorbate_id_many')
                                  ,Arg('ads',1)
                                  ,Arg('struct_id')
                                  ,Arg('ads',0)])]))

pop_ads_compstr = Rule('pop_ads_compstr'
    ,metatemp=PureSQL(["""
            UPDATE adsorbate AS A SET A.composition=
              (select  GROUP_CONCAT(CONCAT('[',C.element_id,',',C.number,']') ORDER BY C.element_id ASC)
                    FROM adsorbate_composition as C
                    WHERE C.adsorbate_id = A.adsorbate_id)"""]))

rules = [populate_adsorbate
             ,pop_struct_ads
             ,pop_ads_compstr]
