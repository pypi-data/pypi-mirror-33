"""
Develop
-------

To setup a development installation one may call either pip as 
follows;
::
   pip install -e .
 
or execute the setup script directly;
::
   python setup.py develop

the pip version is generally preferred.

Documentation
-------------

Documentation may be generated using the setup script.
::
   python setup.py build_sphinx -b singlehtml|html|latex

Select between singleHTML, HTMl and LaTeX as necessary.
The output is saved under :file:`dist/singlehtml|html|latex`.
"""
from setuptools import setup, find_packages
# from distutils.core import setup
from apeman import __meta__
import os

setup(
 name                 = __meta__.__project__,
 version              = __meta__.__release__, 
 description          = 'Overlays for Python',
# long_description     = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
 url                  = 'http://www.manaikan.com/',
 author               = 'Carel van Dam',
 author_email         = 'carelvdam@gmail.com',
 license              = __meta__.__licence__,
 platforms            = 'any',
 install_requires     = ['six',
                         'future',
                         'pathlib;python_version=="2.7"',
                         'mock;python_version=="2.7"'], # See PEP 508 : Environmental Markers
#  scripts            = [],      # Command Line callable scripts e.g. '/Path/To/Script.py'
 packages             = find_packages(exclude=["mockup","tests*","__overlay*","__tiers*","__uppercase*","_complex_","_simple_","_delete_","_example_"]),
 include_package_data = True,
 zip_safe             = False,
 test_suite           = "tests",
 tests_require        = [# 'tox',                             # Uncomment to enable ToX
                         'apeman-overlays',
                         # 'unittest2;python_version=="2.7"', # Six offers a shim that negates the need for unittest2
                        ], 
#  cmdclass             = {'test': Tox}                       # Uncomment to enable ToX
 command_options      = {'build_sphinx': {
                          'version'    : ('setup.py', "0.0"),
                          'release'    : ('setup.py', "0.0.0"),
                          'source_dir' : ('setup.py','docs'),
                          'build_dir'  : ('setup.py','dist'),
                          'config_dir' : ('setup.py','docs'),}}, 
 classifiers          = [ # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
  "Development Status :: 3 - Alpha",
  "Intended Audience :: Developers",
#   "Framework :: Apeman :: Overlay ",
  "Intended Audience :: Developers",
  "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
  "Natural Language :: English",
  "Operating System :: OS Independent",
  "Programming Language :: Python",
  "Programming Language :: Python :: 2",
  "Programming Language :: Python :: 2.7",
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.6",
  "Topic :: Software Development :: Libraries :: Python Modules",
  "Topic :: Utilities",
 ],
)
