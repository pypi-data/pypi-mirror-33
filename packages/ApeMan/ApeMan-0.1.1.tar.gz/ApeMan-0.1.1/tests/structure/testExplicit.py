"""
Explicit
--------

.. note ::

   This was originally called UpperCase but has since been renamed to Structure to indicate it's
   relationship to Scaffold.

.. note ::

   The idea with these tests is to ensure that an overlay may be used to patch an existing scaffold.

These tests ensures the overlay(s) patching the mock up package trees work consistently.
The overlays patch the classes in the respective modules capitalizing their output. 

These tests were meant to ensure the stucture of an overlay matched the wrapped package structure.
Instead they highlighted a nuance in the python import system.
Imports do not work behave like objects.
 
Python treats each import uniquely and does not inspect the local scope for previously loaded modules. 
So the following will typically fail
::

    from package_a import package_b
    from package_b import package_c

This may, possibly, be remedied by importing package_c from within the init file of package_b. 
One does not, however, think that this will work as the import command only receives the supplied module names as strings and not as references. 
It seems all imports therefore occur uniquely and do not know of the existance of prior imports.
 
For this reason the following suite of tests will tend fail on occasion.

.. note :: 

   There ought to be a test for package structure, module structure and namespace structure. 
   That is for the package_X directories (With and without __init__ files) and module_X files. 
   How exactly these are performed uncertain right now but should be fleshed out shortly.
"""
# Python Compatability
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import six
# Unit Testing
import unittest
# Sub processes
from subprocess import Popen, PIPE # check_output as cmd, CalledProcessError
# Serialization
import json
# Mathematics
from random import randint
# System
import os
import sys
from pathlib import Path
if __name__ == "__main__" :
 sys.path.append(str(Path.cwd().parents[0]))
 from  utils import osexec
else :
 from ..utils import osexec
# Regular Expressions
import re

PATH = str(Path(__file__).resolve().parents[2]/'mockup')

def moduleNames(source, sep = '.') : 
 # This functionality is provided by olio.strings.cumstr
 """
 Cumulatively joins string parts together 
 
 >>> cumstr(['a','b','c'])
 ['a','a.b','a.b.c']
 
 .. todo :: 
    
    Deprecate this in favour of :class:`overlays.unittest.mock.modname.Module` 
    or once it's refactored appropriately :class:`overlays.pathlib.Module`.
 """
 return ['.'.join(source[:i+1]) for i in range(0, len(source))]

def importPatterns(parts, mask = "from {} import {}",sep = '.'):
 """
 Randomly join string parts together returning ordered importable tuples.
 
 >>> cumstr(['a','b','c','d'])
 [('a.b','c'),('c','d')]
 >>> cumstr(['a','b','c','d'])
 [('a','b'),('b.c','d')]
 
 Note : This assumes the Python import mechanism depends upon prior imports, this turned out not to be true.
 """
 target = parts.pop(0)
 while parts :
  source  = [target] + [parts.pop(0) for i in range(0, randint(0,len(parts)-1))]
  target  = parts.pop(0)
  yield mask.format(sep.join(source), target)

class testExplicitOverlay(unittest.TestCase):
 """Ensure that the explicit package scaffold may be may be overlayed with an explicit structure

 These tests assert that, at a minimum, ApeMan will correctly overlay explicit scaffolds.
 This is assures that ApeMan

  * is readily importable
  * switches patches for sources
  * supports nested structures.

 The last point is quite subtle; often an ApeMan implementation will substitute a patch for a single, unnested, module but fail to substitute a patch for one nested, one level down, within a packge.
 This is particularly noticeable in Python 2.7 where :meth:`imp.find_module` is sensitive to the provided list of search paths.
 """
 # Originallly : """Tests the explicitly imported overlay"""

 #: Code representing a :file:`__main__.py` file that imports the overlay and the patched module accordingly
 mask = "\n".join([
   "import json",
   "import sys",
   "import {0}",
   "from {1} import Class",
   "print(json.dumps({{'class':str(Class())}}))",
  ]).format
 #: The root path containing the modules and their overlays
 path = str(Path(__file__).resolve().parents[2]/'mockup') # Originally : str(Path(os.path.dirname(os.path.abspath(__file__))).joinpath('../mockup').resolve())

 def testExplicitClassA(self):
  """Asserts imports work under different patterns"""
  result = osexec(self.path, self.mask('explicitImport', "module"))
#   if 'error' in result :
#    self.assertTrue(result['message'] in ["No module named 'package_a'"])
#   else :
  answer = {"class":"MODULE.CLASSA"} # Originally : {"class":".MODULE.CLASSA"} due to an error in mockup/module.py
  self.assertEqual(answer, result)

 def testExplicitClassB(self):
  """Asserts imports work under different patterns"""
  result = osexec(self.path, self.mask('explicitImport', "explicit.module"))
  answer = {"class":"EXPLICIT.MODULE.CLASSB"}
  self.assertEqual(answer, result)

 def testExplicitClassC(self):
  """Asserts imports work under different patterns"""
  result = osexec(self.path, self.mask('explicitImport', "explicit.explicit.module"))
  answer = {"class":"EXPLICIT.EXPLICIT.MODULE.CLASSC"}
  self.assertEqual(answer, result)

 @unittest.skipIf(six.PY2,"Namespaced packages are not supported in Python < 3.4")
 def testImplicitClassC(self):
  """Asserts imports work under different patterns"""
  result = osexec(self.path, self.mask('explicitImport', "explicit.implicit.module"))
  answer = {"class":"EXPLICIT.IMPLICIT.MODULE.CLASSC"}
  self.assertEqual(answer, result)

 def testExplicitClassD(self):
  """Asserts imports work under different patterns"""
  result = osexec(self.path, self.mask('explicitImport', "explicit.explicit.module"))
  answer = {"class":"EXPLICIT.EXPLICIT.MODULE.CLASSC"}
  self.assertEqual(answer, result)


# Note : 
#
# The following tests assert that given a package, A.B.C, it 
# is directly importable at each level both normally, A, A.B
# and A.B.C and via an overlay, overlay.A, overlay.A.B and 
# overlay.A.B.C.
#
#  mask = {
#   "fullpath":
#    "\n".join([
#     "import json",
#     "import sys",
#     "from {} import {}",
#     "print(json.dumps([key for key in sys.modules.keys() if any([part in key for part in {}])]))"
#    ]),
#  }
#
#   source = moduleNames(['uppercase','tiers'])                                    # Ideally : ['uppercase','_tiers_']
#   target = []                                                                    # moduleNames(['tiers']) - 'tiers' is not imported by uppercase.tiers as is done in testTierA
#   result = sorted(source + target) 
#   answer = sorted(osexec(self.mask["fullpath"], "uppercase", "tiers", ["uppercase","tiers"]))
#   source = moduleNames(['explicit','module'])
#   self.assertEqual(answer, result)
#
#  def testTierA(self):
#   """Asserts Class(es) Existence in Overlay"""
#   source = moduleNames(['uppercase','tiers','module_a'])                         # Ideally : ['uppercase','_tiers_','_module_a_']
#   target = moduleNames(['tiers','module_a'])
#   result = sorted(source + target) 
#   answer = sorted(osexec(self.mask["fullpath"], "uppercase.tiers", "module_a", ["uppercase","tiers","module"]))
#   self.assertEqual(answer, result, __doc__)
#
#  def testTierB(self):
#   """Asserts Class(es) Existence in Overlay"""
#   source = moduleNames(['uppercase','tiers','package_a','module_b'])             # Ideally : ['uppercase','_tiers_','_package_a_','_module_b_']
#   target = moduleNames(['tiers','package_a','module_b'])
#   result = sorted(source + target)
#   answer = sorted(osexec(self.mask["fullpath"], "uppercase.tiers.package_a", "module_b", ["uppercase","tiers","module","package"]))
#   self.assertEqual(answer, result, __doc__)
#
#  def testTierC(self):
#   """Asserts Class(es) Existence in Overlay"""
#   source = moduleNames(['uppercase','tiers','package_a','package_b','module_c']) # Ideally : ['uppercase','_tiers_','_module_a_']
#   target = moduleNames(['tiers','package_a','package_b','module_c'])
#   result = sorted(source + target)
#   answer = sorted(osexec(self.mask["fullpath"], "uppercase.tiers.package_a.package_b", "module_c", ["uppercase","tiers","module","package"]))
#   self.assertEqual(answer, result, __doc__)
#
#  def testTierD(self):
#   """Asserts Class(es) Existence in Overlay"""
#   source = moduleNames(['uppercase','tiers','package_a','package_b','package_c','module_d']) # Ideally : ['uppercase','_tiers_','_module_a_']
#   target = moduleNames(['tiers','package_a','package_b','package_c','module_d'])
#   result = sorted(source + target)
#   answer = sorted(osexec(self.mask["fullpath"], "uppercase.tiers.package_a.package_b.package_c", "module_d", ["uppercase","tiers","module","package"]))
#   self.assertEqual(answer, result, __doc__)
#


if __name__ == '__main__':
 unittest.main()
#  import logging
# #  from pprint import pprint
# #  logging.basicConfig(format = '%(message)s') #, level=logging.DEBUG) #, stream=sys.stdout)
# #  logger = logging.getLogger("apeman.apeman") # Specifies the apeman package and apeman module contained therein.
#  logging.basicConfig(level=logging.DEBUG) #, stream=sys.stdout)
# #  logger = logging.getLogger("apeman.__36__") 
# #  logger.setLevel(logging.DEBUG)
# #  target = logging.StreamHandler()
# #  target.setLevel()
# #  format = logging.Formatter('%(message)s')
# #  target.setFormatter(format)
# #  logger.addHandler(target)
# #  pprint(dir(logger.root))
#  try :
# #   pip.main(['install', '-q', '-e', '.'])
#   logfile = Path(__file__).with_suffix(".log")
#   with open(str(logfile),'w') as log :
#    runner = unittest.TextTestRunner(log)
#    unittest.main(testRunner=runner)# , buffer=True, catchbreak=True)
#  finally :
# #   pip.main(['uninstall', '-q', '-y', 'TierTest'])
#   with open(str(logfile),'r') as log :
#    [print(line.rstrip()) for line in log.readlines()]
