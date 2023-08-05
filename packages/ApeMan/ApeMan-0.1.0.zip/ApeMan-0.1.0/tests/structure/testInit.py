"""
__init__ Files
==============

This is a secondary set of tests that affirm that explicit packages within the scaffold contain "file"`__init__.py` files.

.. todo::

   Inadvertently one has been importing the version numbers from the overlays and not those of the original modules.
   This test should be renamed and moved to strcture tests.
"""
from six import PY2, PY3
import unittest
from pathlib import Path
if __name__ == "__main__" :
 import sys; sys.path.insert(0, str(Path(__file__).resolve().parents[1])) # Add the path containing utils to sys.path
 from   utils import osexec, importSimple
else :
 from ..utils import osexec, importSimple

class testExplicitPackages(unittest.TestCase):
 """
 These tests ensure that the explicit packages in the overlay are truly so. 
 They assert that each such package provides an :file:`__init__.py` file.
 """
 # Update : I have swapped out importPatterns for importSimple
 # as the former triggered import errors unrelated to overlays
 
 #: Code representing a :file:`__main__.py` file that imports the overlay and the patched module accordingly
 mask = "\n".join([
   "import json",
   "import sys",
   "import {0}",
   "{1}",
   "print(json.dumps({{'version':{2}}}))",
  ]).format
 #: The root path containing the modules and their overlays
 path = str(Path(__file__).resolve().parents[2]/'mockup') # Originally : str(Path(os.path.dirname(os.path.abspath(__file__))).joinpath('../mockup').resolve())

 def testPackageA(self):
  """Ensure that a :attr:`__version__` is specified for the package"""
  result = osexec(self.path, self.mask('explicitImport', '\n'.join(importSimple(['explicit','__version__'])), "__version__"))
#   if 'error' in result :
#    self.assertTrue(result['message'] in ["No module named 'package_a'"])
#   else :
  answer = {'version':[1,1]}
  self.assertEqual(answer, result)
  
 def testExplicitPackageB(self):
  """Ensure that a :attr:`__version__` is specified for the package"""
  result = osexec(self.path, self.mask('explicitImport', '\n'.join(importSimple(['explicit','explicit','__version__'])), "__version__"))
  answer = {'version':[1,2]}
  self.assertEqual(answer, result)

 @unittest.skipIf(PY2,"Namespaced packages are not supported in Python 2.7")
 def testImplicitPackageB(self):
  """Ensure that a :attr:`__version__` is specified for the package"""
  result = osexec(self.path, self.mask('implicitImport', '\n'.join(importSimple(['implicit','explicit','__version__'])), "__version__"))
  answer = {'version':[1,2]}
  self.assertEqual(answer, result)

 def testPackageC(self):
  # """Asserts imports work under different patterns"""
  """Ensure that a :attr:`__version__` is specified for the package"""
  result = osexec(self.path, self.mask('explicitImport', '\n'.join(importSimple(['explicit','explicit','explicit','__version__'])), "__version__"))
  answer = {'version':[1,3]}
  self.assertEqual(answer, result)

if __name__ == "__main__" :
 unittest.main()