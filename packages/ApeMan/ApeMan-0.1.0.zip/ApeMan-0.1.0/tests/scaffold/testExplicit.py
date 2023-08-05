"""
Explicit Scaffold
-----------------

This test ensures the consistent structure set of packages an modules having the following structure.
The explicit test structure has a main trunk of explicit packages nested within one another and an implicit package branch near the root.
::

   mockup
    explicit/
     explicit/
      explicit/
       __init__.py
       module.py
      __init__.py
      module.py
     implicit 
      module.py
     __init__.py
     module.py
    module.py
"""
# Python 2 Compatability
# from __future__ import absolute_import
# from __future__ import division            # These
# from __future__ import print_function      # seem
# from __future__ import unicode_literals    # to
# from builtins import open                  # be 
# from builtins import str                   # unnecessary
# from future import standard_library
# from pprint import pprint
# standard_library.install_aliases()
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
if __name__ == "__main__" :
 import sys; sys.path.insert(0, str(Path(__file__).resolve().parents[1])) # Make the utils module available to sys.path
 from  utils import osexec, importSimple
else :
#  import sys; sys.path.insert(0, str(Path(__file__).resolve().parents[2]/"mockup")) # Make the utils module available to sys.path
 from ..utils import osexec, importSimple

#: This path identifies the location of the package/module mock up used in the test suite.
PATH = Path(__file__).resolve().parents[2]/"mockup" # Originally : os.path.join(os.path.dirname(os.path.abspath(__file__)),'../mockup')

# @unittest.skipIf(six.PY3 and __name__!="__main__", "Test skipped since unittest mangles sys.path")
@patch("sys.path", copy(sys.path) + [str(PATH)])
class testExplicit(unittest.TestCase) :
 """Ensure the consistent structure of the explicit mockup folder

 These tests assert that the explicit mockup test structure is fixed in it's design
 """

 def setUp(self) :
  """Set up function for unit tests
  """
  self.path = copy(sys.path)
  sys.path.append(str(PATH))

 def tearDown(self) : 
  """Tear down function for unit tests
  """
  sys.path = self.path
  

#  @unittest.skipIf(__name__ != "__main__", "I have no idea why but this test fails if called from the command line e.g. with 'python setup.py unittest discover'") # It is especially perplexing since lower level modules succeed
 def testExplicitClassA(self):
#   """Asserts Class(es) Existence"""
  """Asserts :file:`module.py` exists"""
#   pprint(sys.path)
  from module import Class
  self.assertEqual(str(Class()), 'module.ClassA')

 def testExplicitClassB(self) :
  """Asserts :file:`explicit/module.py` exists"""
#   sys.path.append()
#   with patch("sys.path", [str(Path(__file__).resolve().parents[2]/"mockup"), str(Path(__file__).resolve().parents[2]/"mockup"/"explicit")] + copy(sys.path)) :
#   from importlib.util import find_spec
#   print(find_spec("module").loader.load_module())
#   print(find_spec("explicit").loader.load_module())
#    print(find_spec("explicit.module"))
#    from explicit.module import Class
  from explicit.module import Class
  self.assertEqual(str(Class()), 'explicit.module.ClassB')

 def testExplicitClassC(self) :
  """Asserts :file:`explicit/explicit/module.py` exists         """
  from explicit.explicit.module import Class
  self.assertEqual(str(Class()), 'explicit.explicit.module.ClassC')

 @unittest.skipIf(six.PY2,"Namespaced packages are not supported in Python < 3.4")
 def testImplicitClassC(self) :
  """Asserts :file:`explicit/implicit/module.py` exists         """
  from explicit.implicit.module import Class
  self.assertEqual(str(Class()), 'explicit.implicit.module.ClassC')

 def testExplicitClassD(self) :
  """Asserts :file:`explicit/explicit/explicit/module.py` exists"""
  from explicit.explicit.explicit.module import Class
  self.assertEqual(str(Class()), 'explicit.explicit.explicit.module.ClassD')

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
#  if PY2 :
 unittest.main()
#  if PY3 :
#   try : 
#  #   pip.main(['install', '-q', '-e', '.'])
#    logfile = Path(__file__).with_suffix(".log")
#    with open(str(logfile),'w') as log :
#     runner = unittest.TextTestRunner(log)
#     unittest.main(testRunner=runner)# , buffer=True, catchbreak=True)
#   finally : 
#  #   pip.main(['uninstall', '-q', '-y', 'TierTest'])
#    with open(str(logfile),'r') as log :
#     [print(line.rstrip()) for line in log.readlines()]
  
