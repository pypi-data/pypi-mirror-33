from dbgen.support.datatypes.table      import Table,Col,FK
from dbgen.support.datatypes.rule  import Rule
from dbgen.support.datatypes.misc       import Arg,noIndex
from dbgen.support.datatypes.metatemp   import Block,MetaTemp,SimpleUpdate,PureSQL
from dbgen.support.datatypes.temp       import Temp
from dbgen.support.datatypes.sqltypes   import Varchar,Decimal
from dbgen.support.utils                import mkInsCmd

##########################################################################################

stoich = Table('stoich'
        ,desc = 'Mapping table between jobs and reactions'
        ,cols = [Col('job_id',    pk=True)
                ,Col('rxn_id',    pk=True)
                ,Col('stoich',    nn=True)]
        ,fks = [FK('job_id','relax_job')
               ,FK('rxn_id','rxn')])

rxn = Table('rxn'
        ,desc = 'Any reaction'
        ,cols = [Col('rxn_id',                pk=True,auto=True)
                ,Col('name',        Varchar(),    nn=True,uniq=True)
                ,Col('is_adsorption',        nn=True)
                ,Col('dE',            Decimal())])

ads_triple = Table('ads_triple'
        ,desc='Triples of bare + complex + adsorbate'
        ,cols = [Col('bare_id',                pk=True)
                ,Col('complex_id',             pk=True)
                ,Col('adsorbate_id',           pk=True)
                ,Col('delta_e_surf',Decimal(),   nn=True)
                ,Col('calc_id',                nn=True)
                ,Col('metal_comp',Varchar(),       nn=True)
                ]
        ,fks = [FK('bare_id',       'relax_job',    'job_id')
               ,FK('complex_id',    'relax_job',    'job_id')
               ,FK('adsorbate_id',  'adsorbate',    'adsorbate_id')
               ,FK('calc_id',       'calc',         'calc_id')
               ])
tables = [stoich,rxn,ads_triple]
##########################################################################################
##########################################################################################
##########################################################################################
rxn_energies = Rule('rxn_energies'
    ,query = """SELECT S.rxn_id,SUM(T.energy * S.stoich) AS dE
                    FROM stoich    AS S
                    JOIN rxn         AS R USING (rxn_id)
                    JOIN finaltraj AS T USING (job_id)
                    WHERE R.dE IS NULL
                    GROUP BY S.rxn_id """
    ,metatemp = SimpleUpdate(rxn,['dE']))

################################################
# Pairs of surfaces that differ by an adsorbate
#################################################
pop_ads_triple=Rule('ads_triple'
    ,metatemp=PureSQL(["""
            INSERT INTO ads_triple (bare_id
                                   ,complex_id
                                   ,adsorbate_id
                                   ,delta_e_surf
                                   ,calc_id
                                   ,metal_comp)
                SELECT X.bare_id
                      ,X.complex_id
                      ,A.adsorbate_id
                      ,X.delta_e_surf
                      ,X.calc_id
                      ,X.metal_comp
                FROM
                (SELECT
                        F1.job_id                    AS complex_id
                        ,F2.job_id               AS bare_id
                        ,MIN(F1.energy - F2.energy)  AS delta_e_surf -- MIN actually doesn't matter - schema doesn't know Finaltraj as 1-1 relationship
                        ,J1.calc_id                  AS calc_id
                        ,MIN(S1.metal_comp)          AS metal_comp -- MIN actually doesn't matter
                        , GROUP_CONCAT(CONCAT('[',C.element_id,
                                              ',',C.count - COALESCE(C2.count, 0),
                                              ']')
                                    ORDER BY C.element_id ASC) AS composition
                        FROM
                            finaltraj F1
                                JOIN struct        AS S1  ON F1.struct_id=S1.struct_id
                                JOIN surface       AS SS1 ON S1.struct_id=SS1.struct_id
                                JOIN relax_job     AS J1  ON F1.job_id=J1.job_id
                                JOIN struct        AS S2  USING (metal_comp)
                                JOIN finaltraj     AS F2  ON F2.struct_id=S2.struct_id
                                JOIN relax_job     AS J2  ON F2.job_id=J2.job_id AND J2.calc_id=J1.calc_id
                                JOIN surface       AS SS2 ON S2.struct_id=SS2.struct_id

                                JOIN      struct_composition AS C   ON (C.struct_id=S1.struct_id)
                                LEFT JOIN struct_composition AS C2  ON C2.struct_id = S2.struct_id AND C2.element_id=C.element_id
                        WHERE
                                -- (F1.job_id,F2.job_id) NOT IN (SELECT complex_id,bare_id FROM ads_triple) AND
                                S1.n_atoms > S2.n_atoms
                                AND S1.n_elems >= S2.n_elems
                                AND C.element_id IN (1 , 2, 6, 7, 8)                 -- already know they have same metal stoich -
                                AND C.count - COALESCE(C2.count, 0) != 0 -- ignore in case the have the same # of some nonmetal
                        GROUP BY complex_id,bare_id) AS X
                 JOIN adsorbate  AS A ON A.composition = X.composition

            ON DUPLICATE KEY UPDATE bare_id=X.bare_id"""]))


rules = [rxn_energies,pop_ads_triple]
