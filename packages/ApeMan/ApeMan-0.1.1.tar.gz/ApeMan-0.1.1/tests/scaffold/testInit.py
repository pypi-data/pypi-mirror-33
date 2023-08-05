"""
__init__ Files
==============

This is a secondary set of tests that affirm that explicit packages within the scaffold contain "file"`__init__.py` files.

.. todo::

   Inadvertently one has been importing the version numbers from the overlays and not those of the original modules.
   This test should be moved to test.structure a folder that does not yet exist and a copy of it left here but with
   the correct version numbers in use.
"""
import six
import unittest
from pathlib import Path
if __name__ == "__main__" :
 import sys; sys.path.insert(0, str(Path(__file__).resolve().parents[1])) # Make the utils module available to sys.path
 from  utils import osexec, importSimple
else :
 from ..utils import osexec, importSimple

class testExplicitPackages(unittest.TestCase):
 """Ensure certain package are explcit

 These tests ensure that the explicit packages in the overlay are truly so. 
 They assert that each such package provides an :file:`__init__.py` file.
 
 todo:
  These test do not assert that implicit packages are infact so.
 """
 # Update : I have swapped out importPatterns for importSimple
 # as the former triggered import errors unrelated to overlays
 
 #: Code representing a :file:`__main__.py` file that imports the overlay and the patched module accordingly
 mask = "\n".join([
   "import json",
   "import sys",
   "{0}",
   "print(json.dumps({{'version':{1}}}))",
  ]).format
 #: The root path containing the modules and their overlays
 path = str(Path(__file__).resolve().parents[2]/'mockup') # Originally : str(Path(os.path.dirname(os.path.abspath(__file__))).joinpath('../mockup').resolve())

 def testPackageA(self):
  """Ensure that a :attr:`__version__` is specified for the package"""
  result = osexec(self.path, self.mask('\n'.join(importSimple(['explicit','__version__'])), "__version__"))
#   if 'error' in result :
#    self.assertTrue(result['message'] in ["No module named 'package_a'"])
#   else :
  answer = {'version':[0,1]}
  self.assertEqual(answer, result)
  
 def testExplicitPackageB(self):
  """Ensure that a :attr:`__version__` is specified for the package"""
  result = osexec(self.path, self.mask('\n'.join(importSimple(['explicit','explicit','__version__'])), "__version__"))
  answer = {'version':[0,2]}
  self.assertEqual(answer, result)

 @unittest.skipIf(six.PY2,"Namespaced packages are not supported in Python 2.7")
 def testImplicitPackageB(self):
  """Ensure that a :attr:`__version__` is specified for the package"""
  result = osexec(self.path, self.mask('\n'.join(importSimple(['implicit','explicit','__version__'])), "__version__"))
  answer = {'version':[0,2]}
  self.assertEqual(answer, result)

 def testPackageC(self):
  # """Asserts imports work under different patterns"""
  """Ensure that a :attr:`__version__` is specified for the package"""
  result = osexec(self.path, self.mask('\n'.join(importSimple(['explicit','explicit','explicit','__version__'])), "__version__"))
  answer = {'version':[0,3]}
  self.assertEqual(answer, result)

if __name__ == "__main__" :
 unittest.main()