import setuptools, re # type: ignore

with open('adsorber/__init__.py') as fd:
    version = re.search("__version__ = '(.*)'", fd.read()).group(1)

setuptools.setup(
    name="CC-Adsorber"
    ,version=version
    ,url="https://github.com/statt8900/Adsorber"
    ,author="Michael Statt"
    ,author_email="mstatt@stanford.edu, ksb@stanford.edu"
    ,description="Tools for computational catalyst research"
    ,license='APACHE LICENSE, VERSION 2.0'
    ,packages=['adsorber'
             ,'adsorber.gui'
             ,'adsorber.objects'
    ]
    ,install_requires=['ase'
                      ,'pymatgen'
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
