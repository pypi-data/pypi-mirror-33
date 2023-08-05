"""
Implicit Scaffold
-----------------

The imlpicit structure is simply the mirror of the explicit one.
::

   mockup
    implicit
     explicit
      __init__.py
      module.py
     implicit
      implicit
       module.py
      module.py
     module.py
    module.py
"""
# Python 2 Compatability
# from __future__ import absolute_import
# from __future__ import division
from __future__ import print_function
import six
from copy import copy
# Normal imports
# System
import os
import sys
from pathlib import Path
# Testing
import unittest
if six.PY2 :
#  import unittest2 as unittest
 from mock import patch
if six.PY3 :
#  import unittest
 from unittest.mock import patch
# Temp
# import tempfiles

#: This path identifies the location of the package/module mock up used in the test suite.
PATH = Path(__file__).resolve().parents[2]/"mockup" # Originally : os.path.join(os.path.dirname(os.path.abspath(__file__)),'../mockup')

# @unittest.skip("Meh")
@unittest.skipIf(six.PY2,"Namespaced packages are not supported in Python 2.7")
# @unittest.skipIf(six.PY3 and __name__ != "__main__","Namespaced packages are not supported in Python 2.7")
@patch("sys.path", [str(PATH)] + copy(sys.path))
class testImplicit(unittest.TestCase) :
 """Ensure the consistent structure of the implicit mockup folder

 These tests assert that the explicit mockup test structure is fixed in it's design

 Note : 
  Python 2.7 does not support implicit packages (Namespaced packages per :PEP:420) and all the tests fail.
  Interestingly it seems to fail in order so :mod:`implicit.implicit.implicit.module` will fail to import with an import error saying it does not exist.
  Adding an init file to the first namespace results in an error stating that :mod:`implicit.implicit.module` does not exist; repeating the process successively reports that :mod:`implicit.module` and :mod:`module` do not exist.
 """

#  def setUp(self) :
#   """Set up function for unit tests
#   """
#   print("\n"+str(sys.path)+"\n")

#  def tearDown(self) : 
#   """Tear down function for unit tests
#   """

#  @unittest.skipIf(__name__ != "__main__", "I have no idea why but this test fails if called from the command line e.g. with 'python setup.py unittest discover'") # It is especially perplexing since lower level modules succeed
 def testImplicitClassA(self) :
  """Asserts :file:`module.py` exists"""
  # Note : There is an init file in the tiers folder.
  from module import Class
  self.assertEqual(str(Class()), 'module.ClassA')

 def testImplicitClassB(self) :
  """Asserts :file:`implicit/module.py` exists"""
#   print(sys.path)
#   from importlib.machinery import find_module
#   print(find_module("implicit"))
  from implicit.module import Class
  self.assertEqual(str(Class()), 'implicit.module.ClassB')

 def testImplicitClassC(self) :
  """Asserts :file:`implicit/implicit/module.py` exists"""
  from implicit.implicit.module import Class
  self.assertEqual(str(Class()), 'implicit.implicit.module.ClassC')

 def testExplicitClassC(self) :
  """Asserts :file:`implicit/explicit/module.py` exists"""
  from implicit.implicit.module import Class
  self.assertEqual(str(Class()), 'implicit.implicit.module.ClassC')

 def testImplicitClassD(self) :
  """Asserts :file:`implicit/implicit/implicit/module.py` exists"""
  from implicit.implicit.implicit.module import Class
#   pprint(sys.path)
  self.assertEqual(str(Class()), 'implicit.implicit.implicit.module.ClassD')

if __name__ == '__main__':
 from pathlib import Path
 from pprint import pprint
 import logging
 logging.basicConfig(format = '%(message)s', level=logging.DEBUG)#, stream=sys.stdout)
#  logger = logging.getLogger("apeman")
#  logger.setLevel(logging.DEBUG)
#  target = logging.StreamHandler()
#  target.setLevel()
#  format = logging.Formatter('%(message)s')
#  target.setFormatter(format)
#  logger.addHandler(target)
#  pprint(dir(logger.root))
 try : 
#   pip.main(['install', '-q', '-e', '.'])
  logfile = Path(__file__).with_suffix(".log")
  with open(str(logfile),'w') as log :
   runner = unittest.TextTestRunner(log)
   unittest.main(testRunner=runner)# , buffer=True, catchbreak=True)
 finally : 
#   pip.main(['uninstall', '-q', '-y', 'TierTest'])
  with open(str(logfile),'r') as log :
   [print(line.rstrip()) for line in log.readlines()]
  