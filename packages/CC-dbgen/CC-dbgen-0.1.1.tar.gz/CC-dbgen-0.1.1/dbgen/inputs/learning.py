from dbgen.support.datatypes.table      import Table,Col,FK
from dbgen.support.datatypes.rule       import Rule
from dbgen.support.datatypes.sqltypes   import Varchar,Decimal

##########################################################################################
##########################################################################################
##########################################################################################

model = Table('model'
    ,desc = 'linear regression models'
    ,cols = [Col('id',            pk = True,auto = True)
            ,Col('name',Varchar(),nn = True)])

hyperparameter = Table('hyperparameter'
    ,desc='List of triplestore values (FK''d from hyperparameter_value)'
    ,cols = [Col('hyperparameter_id',pk = True,auto = True)
            ,Col('name',Varchar())])

hyperparameter_value = Table('hyperparameter_value'
    ,desc='Triplestore table describing hyperparameters for a machine learning application'
    ,cols = [Col('hyperparameter_id',pk = True,auto = True)
            ,Col('name', Varchar(),  nn = True,uniq = True)
            ,Col('value',Varchar())]
    ,fks = [FK('hyperparameter_id','hyperparameter')
            ,FK('name','hyperparameter_type')])

hyperparameter_type = Table('hyperparameter_type'
    ,desc="We'll be dogmatic here and have a universal mapping between hyperparameter names and datatypes"
    ,cols = [Col('name',    Varchar(), pk = True)
            ,Col('datatype',Varchar(), nn = True)])

struct_dataset = Table('struct_dataset'
    ,desc = 'Data to be used for machine learning that is associated with a chemical species'
    ,cols = [Col('struct_dataset_id',pk = True, auto = True)
            ,Col('name',Varchar(),   nn = True, uniq = True)])

struct_dataset_element = Table('struct_dataset_element'
    ,desc ='A fact about some chemical species from a dataset'
    ,cols = [Col('struct_dataset_id',           pk = True)
            ,Col('species_id',                  pk = True)
            ,Col('property',        Varchar(),  pk = True)
            ,Col('value',           Decimal(),  nn = True)]
    ,fks  = [FK('struct_dataset_id','struct_dataset')
            ,FK('species_id',       'species')])

rxn_dataset  = Table('rxn_dataset'
    ,desc = 'Data to be used for machine learning that is associated with a chemical species'
    ,cols = [Col('rxn_dataset_id',  pk = True,auto = True)
            ,Col('name',Varchar(),  nn = True,uniq = True)])

rxn_dataset_element = Table('rxn_dataset_element'
    ,desc = 'A fact about some chemical species from a dataset'
    ,cols = [Col('rxn_dataset_id',          pk = True)
            ,Col('rxn_id',                  pk = True)
            ,Col('property',    Varchar(),  nn = True)
            ,Col('value',       Decimal(),  nn = True)]
    ,fks  = [FK('rxn_dataset_id','rxn_dataset')
            ,FK('rxn_id','rxn')])

tables = [hyperparameter
         ,hyperparameter_type
         ,hyperparameter_value
         ,struct_dataset
         ,struct_dataset_element
         ,rxn_dataset
         ,rxn_dataset_element]
##########################################################################################
##########################################################################################
##########################################################################################

rules = [] # type: list
