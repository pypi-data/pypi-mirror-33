# External Modules
from copy import deepcopy
# Internal modules
from dbgen.support.datatypes.table     import Table,Col,FK
from dbgen.support.datatypes.rule import Rule
from dbgen.support.datatypes.metatemp  import PureSQL
from dbgen.support.datatypes.sqltypes  import Varchar,Decimal
from dbgen.core.lists                  import flatten


##########################################################################################

#Refeng tables
#-------------
ref_scheme = Table('ref_scheme'
    ,desc = 'A set of rules to determine when a struct is a valid reference state.'
    ,cols =[Col('ref_scheme_id', pk = True,auto = True)
           ,Col('name',Varchar(),    nn = True,uniq = True)])

ref_scheme_elem = Table('ref_scheme_elem'
    ,desc = 'For each reference scheme and each element, specify the symmetry needed'
    ,cols = [Col('ref_scheme_id',    pk=True)
            ,Col('element_id',        pk=True)
            ,Col('symmetry',Varchar(),    nn=True)]
    ,fks  = [FK('ref_scheme_id','ref_scheme')
            ,FK('element_id',   'element')])

ref_scheme_stoich = Table('ref_scheme_stoich'
    ,desc = """For each reference scheme and each element, specify the reduced stoichiometry needed.
               This is essentially a constraint on which jobs are regarded as reference states for a given element."""
    ,cols=[Col('ref_scheme_id',        pk=True)
          ,Col('element_id',        pk=True)
          ,Col('component_id',        pk=True)
          ,Col('count',                nn=True)]
    ,fks = [FK(['ref_scheme_id','element_id'],'ref_scheme_elem')
           ,FK('component_id',  'element',    'element_id')])

ref_scheme_reqs =Table('ref_scheme_reqs'
    ,desc = """For each reference scheme and each element, specify the combination of reference jobs required to calculate the energy per atom.
This is essentially 'precomputing' the matrix problem that would normally be need to be solved.
If element 8 has (8,1),(1,-2) it would mean:
    The energy per atom for an oxygen atom is 1* normalized energy of job identified as reference for oxygen
                                             -2* normalized energy of job identified as reference for hydrogen
Where the 'normalized energy' of a reference job for element X is the raw energy of that job divided by its count for X
(This normalization trick is to allow us to use primitive/unit cells interchangably)"""
    ,cols=[Col('ref_scheme_id',        pk=True)
          ,Col('element_id',        pk=True)
          ,Col('component_id',        pk=True)
          ,Col('coef',Decimal(),        nn=True)]
    ,fks = [FK(['ref_scheme_id','element_id'],'ref_scheme_elem')
           ,FK('component_id',   'element',   'element_id')])

ref_scheme_refstruct = Table('ref_scheme_refstruct'
    ,desc = 'Warehouse of every structure that is a reference for some refscheme'
    ,cols = [Col('ref_scheme_id',    pk=True)
            ,Col('element_id',       pk=True)
            ,Col('struct_id',        pk=True)]
    ,fks  = [FK(['ref_scheme_id','element_id'],'ref_scheme_elem')
            ,FK('struct_id','struct')])

ref_scheme_job = Table('ref_scheme_job'
    ,desc= """For each element x calc x component, list the job and other useful
                info for calculating energies """
    ,cols = [Col('ref_scheme_id',    pk=True)  #  are
            ,Col('element_id',       pk=True)  #  absolutely
            ,Col('component_id',     pk=True)  #  necessary
            ,Col('job_id',           pk=True)  #  !
            ,Col('calc_id',          nn=True)
            ,Col('calc_other_id',    nn=True)
            ,Col('coef',             nn=True)
            ,Col('energy',Decimal(),   nn=True)
            ]
    ,fks = [FK(['ref_scheme_id','element_id','component_id'],'ref_scheme_reqs')
           ,FK('job_id','relax_job')
           ,FK('calc_id','calc')
           ,FK('calc_other_id','calc_other')])


tables = [ref_scheme,ref_scheme_elem, ref_scheme_job
         ,ref_scheme_refstruct,ref_scheme_reqs
         ,ref_scheme_stoich]


##########################################################################################
##########################################################################################
##########################################################################################
syms = {'2'   : [15]
       ,'14'  : [34]
       ,'64'  : [31,53]
       ,'70'  : [16]
       ,'139' : [49]
       ,'141' : [50]
       ,'152' : [52]
       ,'166' : [5,33,51,62,80]
       ,'194' : [4,12,21,22,27,30,39,40,43,44,48,57,58,59,60,61,64,65,66,67,68,69,71,72,75,76,81]
       ,'225' : [13,20,28,29,32,38,45,46,47,70,77,78,79,82]
       ,'227' : [14]
       ,'229' : [3,11,19,23,24,25,26,37,41,42,55,56,63,73,74]
       ,'C*v' : [6]
       ,'C2v' : [8]
       ,'D*h' : [1,7,9,17,35]
       ,'K*h' : [2,10,18,36,54]}

syms2 = deepcopy(syms)
syms2['227'].append(syms2['C*v'].pop())
syms2['D*h'].append(syms2['C2v'].pop())

allelems = flatten(list(syms.values()))
ref_scheme_elem_inserts = """INSERT INTO ref_scheme_elem (ref_scheme_id,element_id,symmetry)
                             VALUES %s ON DUPLICATE KEY UPDATE ref_scheme_id=ref_scheme_id
                             """%(','.join(flatten([["(1,%s,'%s')"%(x,y)
                                        for x in xs] for y,xs in syms.items()])
                                        +flatten([["(2,%s,'%s')"%(x,y)
                                                       for x in xs] for y,xs in syms2.items()])))
ref_scheme_stoich_inserts = """INSERT INTO ref_scheme_stoich (ref_scheme_id,element_id,component_id,count)
                               VALUES (1,6,6,1),(1,6,8,1),(1,8,1,2),(1,8,8,1)
                               ,%s ON DUPLICATE KEY UPDATE ref_scheme_id=ref_scheme_id
                               """%(','.join(['(1,{0},{0},1)'.format(i) for i in range(1,83) if i not in [6,8]]
                                               +['(2,{0},{0},1)'.format(i) for i in range(1,83)]))

ref_scheme_req_inserts = """INSERT INTO ref_scheme_reqs (ref_scheme_id,element_id,component_id,coef)
                               VALUES (1,6,6,1),(1,6,8,-1),(1,6,1,2)
                                        ,(1,8,1,-2),(1,8,8,1)
                               ,%s ON DUPLICATE KEY UPDATE ref_scheme_id=ref_scheme_id
                               """%(','.join(['(1,{0},{0},1)'.format(i) for i in range(1,83) if i not in [6,8]]
                                               +['(2,{0},{0},1)'.format(i) for i in range(1,83)]))

default_refscheme = Rule('default_refscheme'
    ,metatemp=PureSQL(["""INSERT INTO ref_scheme (name) VALUES ('default'),('pure')
                            ON DUPLICATE KEY UPDATE ref_scheme_id=ref_scheme_id"""
                      ,ref_scheme_elem_inserts
                      ,ref_scheme_stoich_inserts
                      ,ref_scheme_req_inserts]))


populate_refs = Rule('populate_refs'
     ,metatemp = PureSQL([
    """INSERT INTO ref_scheme_refstruct (ref_scheme_id
                                ,element_id
                                ,struct_id)
    SELECT R.ref_scheme_id
                        ,R.element_id
                        ,S.struct_id
    FROM ref_scheme_elem  AS R
      JOIN ref_scheme_stoich  AS RS ON RS.ref_scheme_id = R.ref_scheme_id AND  RS.element_id = R.element_id
      JOIN  struct   AS S ON R.symmetry=S.symmetry
      JOIN struct_composition AS C ON C.struct_id=S.struct_id AND C.element_id = RS.component_id

        WHERE S.struct_id in (SELECT struct_id from finaltraj)
        GROUP BY S.struct_id,R.ref_scheme_id,R.element_id
        HAVING GROUP_CONCAT(CONCAT('[',RS.component_id,',',RS.count,']'))
              = GROUP_CONCAT(CONCAT('[',C.element_id,',',C.count_norm,']'))

        ON DUPLICATE KEY UPDATE ref_scheme_id=ref_scheme_id"""]))

pop_rsjob = Rule('populate_refscheme_job'
    ,metatemp=PureSQL(["""
        INSERT INTO ref_scheme_job (ref_scheme_id
                                   ,element_id
                                   ,component_id
                                   ,coef
                                   ,job_id
                                   ,energy
                                   ,calc_id
                                   ,calc_other_id)
        SELECT R.ref_scheme_id
               ,R.element_id
               ,R.component_id
               ,R.coef
               ,F.job_id
               ,F.energy
               ,J.calc_id
               ,J.calc_other_id
        FROM
        ref_scheme_reqs           AS R
        JOIN ref_scheme_refstruct AS S ON R.component_id=S.element_id AND R.ref_scheme_id = S.ref_scheme_id
        JOIN finaltraj            AS F USING (struct_id) -- (job,step#,energy)
        JOIN relax_job            AS J USING (job_id)

        ON DUPLICATE KEY UPDATE ref_scheme_id=R.ref_scheme_id
        """]))



rules = [default_refscheme
             ,populate_refs
             ,pop_rsjob]
