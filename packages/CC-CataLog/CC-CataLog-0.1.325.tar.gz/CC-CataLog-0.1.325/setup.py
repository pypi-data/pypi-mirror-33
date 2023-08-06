import setuptools, re # type: ignore

with open('catalog/__init__.py') as fd:
    version = re.search("__version__ = '(.*)'", fd.read()).group(1)

setuptools.setup(
    name="CC-CataLog"
    ,version=version
    ,url="https://github.com/statt8900/CataLog"
    ,author="Michael Statt, Kris Brown"
    ,author_email="mstatt@stanford.edu, ksb@stanford.edu"
    ,description="Tools for computational catalyst research"
    ,license='APACHE LICENSE, VERSION 2.0'
    ,packages=['catalog'
             ,'catalog.data'
             ,'catalog.datalog'
             ,'catalog.fw'
             ,'catalog.gendata'
             ,'catalog.gui'
             ,'catalog.jobs'
             ,'catalog.misc'
             ,'catalog.cli'
    ]
    ,include_package_data=True
    ,entry_points={'console_scripts': ['catalog=catalog.cli.main:main']}
    ,install_requires=['ase==3.16'
                      ,'numpy'
                      ,'pymysql'
                      ,'sqlparse'
                      ,'python-sql'
                      ,'pymatgen'
                      ,'networkx'
                      ,'plotly==2.7'
                      ,'fireworks'
                      ,'mysqlclient==1.3.13'
                      ,'PyQt5==5.11.2'
                      ,'qdarkstyle'
                      ,'prettytable'
                      ,'CC-Adsorber'
                      ,'CC-dbgen'
    ]
    ,python_requires='>3.6, <4'
    ,classifiers=[
        'Development Status :: 4 - Beta'
       ,'Intended Audience :: Developers'
       ,'Topic :: Scientific/Engineering :: Chemistry'
       ,'Programming Language :: Python :: 3.6'
    ]
)
