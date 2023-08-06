import setuptools, re # type: ignore

with open('dbgen/__init__.py') as fd:
    version = re.search("__version__ = '(.*)'", fd.read()).group(1)

setuptools.setup(
    name="CC-dbgen"
    ,version=version
    ,url="https://github.com/ksb/dbgen"
    ,author="Kris Brown"
    ,author_email="ksb@stanford.edu"
    ,description="Tools for computational catalyst research"
    ,license='APACHE LICENSE, VERSION 2.0'
    ,packages=['dbgen'
              ,'dbgen.core'
              ,'dbgen.data'
              ,'dbgen.inputs'
              ,'dbgen.new_inputs'
              ,'dbgen.scripts'
              ,'dbgen.scripts.IO'
              ,'dbgen.scripts.Pure'
              ,'dbgen.scripts.Pure.Atoms'
              ,'dbgen.scripts.Pure.Graph'
              ,'dbgen.scripts.Pure.Load'
              ,'dbgen.scripts.Pure.Misc'
              ,'dbgen.scripts.Pure.Rxns'
              ,'dbgen.support'
    ]
    ,include_package_data=True
    # ,entry_points={'console_scripts': ['catalog=catalog.cli.main:main']}
    ,install_requires=['ase'
    ,'sqlparse'
    ,'networkx'
    ,'python-sql'
    ,'mysqlclient'
    ,'pymatgen'
    ,'tqdm'
    ,'PyOpenGL'
    ,'PyQt5'
    ]
    ,python_requires='>3.6, <4'
    ,classifiers=[
        'Development Status :: 4 - Beta'
       ,'Intended Audience :: Developers'
       ,'Topic :: Scientific/Engineering :: Chemistry'
       ,'Programming Language :: Python :: 3.6'
    ]
)
