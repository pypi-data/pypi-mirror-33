from dbgen.support.datatypes.object     import Object,Attr,Universe
from dbgen.support.datatypes.sqltypes   import SQLType,Int,Varchar,Text,Decimal
from dbgen.support.datatypes.constraint import *
"""
Object-based model, gets processed into Tables/Rules
"""
################################################################################
alljob = Object(name='alljob'
    ,desc = 'DFT jobs'
    ,attr = [Attr('logfile',          Varchar()       ,nnull=True)
            ,Attr('stordir',          Varchar()       ,nnull=True)
            ,Attr('code',             Varchar()       ,nnull=True)
            ,Attr('user',             Varchar())
            ,Attr('timestamp')
            ,Attr('working_directory',Varchar())
            ,Attr('log',              Text('long'))
            ,Attr('pwinp',            Text())
            ,Attr('potcar',           Text('long'))
            ,Attr('poscar',           Text())
            ,Attr('kptcar',           Text())
            ,Attr('paramdict',        Text('long'))
            ,Attr('anytraj',          Text('long'))
            ,Attr('job_type',         Varchar()       ,ind=True)
            ,Attr('job_name',         Varchar())
            ,Attr('ads_catalog',      Varchar())
            ,Attr('structure_catalog',Varchar())
            ,Attr('deleted', nnull=True,ind=True,default=0)]
    ,uniqattr = ['logfile'])

calc = Object(name = 'calc'
    ,desc = 'DFT calc parameters'
    ,attr = [Attr('dftcode',   Varchar(), nnull = True)
            ,Attr('xc',        Varchar(), nnull = True)
            ,Attr('pw',                   nnull = True)
            ,Attr('psp',       Varchar(), nnull = True)]
    ,uniqattr = ['dftcode','xc','pw','psp'])

calc_other= Object('calc_other'
    ,desc = 'Less important DFT Calculator Parameters'
    ,attr = [Attr("kx")
            ,Attr("ky")
            ,Attr("kz")
            ,Attr("fmax",            Decimal())
            ,Attr("econv",           Decimal(10,7))
            ,Attr("dw")
            ,Attr("sigma",           Decimal(10,7))
            ,Attr("nbands")
            ,Attr("mixing",          Decimal())
            ,Attr("nmix")
            ,Attr("xtol",            Decimal(10,7))
            ,Attr("strain",          Decimal())
            ,Attr("gga",             Varchar())
            ,Attr("luse_vdw")
            ,Attr("zab_vdw",         Decimal())
            ,Attr("nelmdl")
            ,Attr("gamma")
            ,Attr("dipol",           Varchar())
            ,Attr("algo",            Varchar())
            ,Attr("ibrion")
            ,Attr("prec",            Varchar())
            ,Attr("ionic_steps")
            ,Attr("lreal",           Varchar())
            ,Attr("lvhar")
            ,Attr("diag",            Varchar())
            ,Attr("spinpol")
            ,Attr("dipole")
            ,Attr("maxstep")
            ,Attr("delta",           Decimal())
            ,Attr("mixingtype",      Varchar())
            ,Attr("bonded_inds",     Varchar())
            ,Attr("energy_cut_off",  Decimal())
            ,Attr("step_size",       Decimal())
            ,Attr("spring",          Decimal())
            ,Attr('cell_dofree',     Varchar())
            ,Attr('cell_factor',     Decimal())
            ,Attr("kpts",            Varchar())])

relax_job = Object(name = 'relax_job'
    ,desc       = 'Jobs that compute local minima for electronic energy'
    ,parents    = ['alljob']
    ,components = ['calc','calc_other']
    ,attr       = [Attr('reference')
                  ,Attr('is_tom')])

roots = Object('roots'
    ,desc = 'Directories which are recursively searched for computation logfiles'
    ,attr = [Attr('root', Varchar(),nnull=True)
            ,Attr('code', Varchar(),nnull=True)
            ,Attr('label',Varchar(),nnull=True)
            ,Attr('active',         nnull=True,default=1)]
    ,uniqattr = ['root','code','label'])


cell = Object('cell'
    ,desc = 'Periodic cells defined by three vectors'
    ,attr = [Attr('a0',          Decimal(),nnull = True)
            ,Attr('a1',          Decimal(),nnull = True)
            ,Attr('a2',          Decimal(),nnull = True)
            ,Attr('b0',          Decimal(),nnull = True)
            ,Attr('b1',          Decimal(),nnull = True)
            ,Attr('b2',          Decimal(),nnull = True)
            ,Attr('c0',          Decimal(),nnull = True)
            ,Attr('c1',          Decimal(),nnull = True)
            ,Attr('c2',          Decimal(),nnull = True)
            ,Attr('surface_area',Decimal())
            ,Attr('volume',      Decimal())
            ,Attr('a',           Decimal())
            ,Attr('b',           Decimal())
            ,Attr('c',           Decimal())]
    ,uniqattr= ['a0','a1','a2','b0','b1','b2','c0','c1','c2'])


pure_struct = Object('pure_struct'
    ,desc = 'Structure abstraction developed by Ankit Jain'
    ,attr = [Attr('name',            Varchar(),  nnull = True)
            ,Attr('spacegroup')
            ,Attr('free')
            ,Attr('nickname',        Varchar())
            ]
    ,uniqattr = ['name'])

species = Object('species'
    ,desc="""A combination of composition and structural information (no floats)"""
    ,attr=[Attr('name',          Varchar())
          ,Attr('nickname',      Varchar())
          ,Attr('composition',   Varchar())]
    ,uniqattr = ['name'])


struct = Object('struct'
    ,desc       = 'List of unique combinations of [atom] and cell'
    ,components = ['cell','pure_struct','pure_struct','species']
    ,attr = [Attr('raw',             Text(),    nnull  = True)
            ,Attr('rawhash',         Varchar(), nnull  = True)
            ,Attr('system_type',     Varchar(), ind    = True) # used to partition subclasses
            ,Attr('n_atoms')
            ,Attr('n_elems')
            ,Attr('composition',     Varchar())
            ,Attr('composition_norm',Varchar())
            ,Attr('metal_comp',      Varchar())
            ,Attr('str_symbols',     Varchar())
            ,Attr('str_constraints', Varchar())
            ,Attr('symmetry',        Varchar())
            ,Attr('pure_struct_id_catalog')
            ,Attr('spacegroup')
            ,Attr('geo_graph',       Text('long'))
            ,Attr('elemental')]
        ,uniqattr= ['rawhash'])


traj = Object('traj'
    ,desc       = 'A step in a relaxation'
    ,parents    = ['alljob']
    ,components = ['struct']
    ,attr = [Attr('final',                   nnull  = True)
            ,Attr('energy',        Decimal(),ind    = True)
            ,Attr('fmax',          Decimal())
            ,Attr('kptden_x',      Decimal())
            ,Attr('kptden_y',      Decimal())
            ,Attr('kptden_z',      Decimal())]
    ,many_to_one = True)

element = Object('element'
    ,desc = 'ID = atomic number' # table for storing data in element.json
    ,attr = [Attr('symbol',                 Varchar(),  nnull = True)
            ,Attr('atomic_weight',          Decimal(),nnull = True)
            ,Attr('name',                   Varchar(),  nnull = True)
            ,Attr('atomic_radius')
            ,Attr('phase',                  Varchar())
            ,Attr('group_id')
            ,Attr('period')
            ,Attr('pointgroup',             Varchar())
            ,Attr('spacegroup')
            ,Attr('evaporation_heat',        Decimal())
            ,Attr('melting_point',           Decimal())
            ,Attr('metallic_radius',         Decimal())
            ,Attr('vdw_radius',              Decimal())
            ,Attr('density',                 Decimal())
            ,Attr('en_allen',                Decimal())
            ,Attr('is_radioactive')
            ,Attr('lattice_struct',          Varchar())
            ,Attr('fusion_heat',             Decimal())
            ,Attr('econf',                   Varchar())
            ,Attr('covalent_radius_bragg',   Decimal())
            ,Attr('geochemical_class',       Varchar())
            ,Attr('abundance_crust',         Decimal())
            ,Attr('heat_of_formation',       Decimal())
            ,Attr('electron_affinity',       Decimal())
            ,Attr('atomic_volume',           Decimal())
            ,Attr('boiling_point',           Decimal())
            ,Attr('proton_affinity',         Decimal())
            ,Attr('covalent_radius_slater',  Decimal())
            ,Attr('lattice_constant',        Decimal())
            ,Attr('dipole_polarizability',   Decimal())
            ,Attr('en_ghosh',                Decimal())
            ,Attr('thermal_conductivity',    Decimal())
            ,Attr('en_pauling',              Decimal())
            ,Attr('gas_basicity',            Decimal())
            ,Attr('abundance_sea',           Decimal())])

adsorbate = Object('adsorbate'
    ,desc     = 'Species that can adsorb onto a surface'
    ,attr     = [Attr('name',        Varchar(),  nnull = True)
                ,Attr('composition', Varchar())]
    ,uniqattr = ['name'])

adsorbate_composition = Object('adsorbate_composition'
    ,'Components of an adsorbate'
    ,parents = ['adsorbate','element']
    ,attr    = [Attr('number', nnull = True)])

struct_adsorbate = Object('struct_adsorbate'
    ,desc        = 'An adsorbate considered on a particular surface'
    ,parents     = ['struct','adsorbate']
    ,many_to_one = True
    ,attr        = [Attr('site', Varchar())])

atom = Object('atom'
    ,desc        = 'List of atoms in unique structs'
    ,parents     = ['struct']
    ,many_to_one = True
    ,components  = ['element','struct_adsorbate']
    ,attr = [Attr('x',            Decimal(),    nnull = True)
            ,Attr('y',            Decimal(),    nnull = True)
            ,Attr('z',            Decimal(),    nnull = True)
            ,Attr('constrained')
            ,Attr('magmom',       Decimal())
            ,Attr('tag')
            ,Attr('v3'),Attr('v4'),Attr('v5'),Attr('v6')
            ,Attr('v7'),Attr('v8'),Attr('v9'),Attr('v10')
            ,Attr('layer')])


chargemol_job = Object('chargemol_job'
        ,desc = 'Jobs that compute bond order analysis with Chargemol'
        ,parents = ['alljob']
        ,components= ['calc','struct']
        ,attr = [Attr('bonddata',Text('long'))])

bond = Object('bond'
    ,desc        = "A bond between two atoms identified by chargemol"
    ,parents     = ['chargemol_job','atom1','atom2']
    ,many_to_one =  True
    ,attr = [Attr('bondorder',Decimal(), nnull = True)
            ,Attr('distance', Decimal(), nnull = True)
            ,Attr('pbc_x',               nnull = True)
            ,Attr('pbc_y',               nnull = True)
            ,Attr('pbc_z',               nnull = True)
            ,Attr('h_bond')])

uni = Universe([alljob
                ,relax_job
                ,roots
                ,calc
                ,calc_other
                ,traj
                ,struct
                ,cell
                ,element
                ,atom
                ,adsorbate
                ,adsorbate_composition
                ,struct_adsorbate
                ,pure_struct
                ,species
                ,chargemol_job

                ])
