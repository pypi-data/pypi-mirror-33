"""
Persistence
-----------

This test ascertains the order of persistence of a class instantiated within a module.
"""
# # Python 2.7 Compatability
# from __future__ import unicode_literals
# from __future__ import print_function
# from __future__ import division
# from __future__ import absolute_import
# from builtins import str
# from builtins import super
# from future import standard_library
# standard_library.install_aliases()
import six
# Normal Imports
import builtins
import os
import inspect
import sys
# from apeman        import Import
import unittest
if six.PY2 :
#  import unittest2 as unittest
 from mock import patch
 unittest.SkipTest("Really be sure the test is skipped")
#  from pathlib import Path
if six.PY3 :
#  from unittest      import TestCase, main
#  import overlays
 from unittest.mock import patch
 from pathlib import Path

 
 mod = \
 """
# print(dir())
# print(__file__)
class Class():
 def __str__(self) :
  return "{name}"
 """.format(name = __name__)
 
 pkg = \
 """
# print(dir())
# print(__file__)
from apeman import Import as ApeMan
ApeMan(name = '{name}', root = '{root}')
 """.format(name="package", root = str(Path.cwd()/"overlay"))
 
 _mod_ = \
 """
# print(dir())
# print(__file__)
from module import *

class Class(Class) :
 def __str__(self) :
  return "Overlayed : {}".format(super().__str__())
 """
 
 # src=\
 # """
 # import package
 # from module import Class
 # Class()
 # """
 
 # Patch for Import.__init__ 
 # def import_init(self, *args, **kvps) : # Python 3 : def import_init(self, *args, name = None, path = None, root = None, _import_ = builtins.__import__, debug = False, **kvps) :
 #  # Python 2 Compatability
 #  if 'debug' in kvps: debug = kvps['debug']; del kvps['debug']
 #  else: debug =  False
 #  if '_import_' in kvps: _import_ = kvps['_import_']; del kvps['_import_']
 #  else: _import_ =  builtins.__import__
 #  if 'root' in kvps: root = kvps['root']; del kvps['root']
 #  else: root =  None
 #  if 'path' in kvps: path = kvps['path']; del kvps['path']
 #  else: path =  None
 #  if 'name' in kvps: name = kvps['name']; del kvps['name']
 #  else: name =  None
 #  # Normal Code
 #  super(Import, self).__init__(*args, **kvps)
 #  # Properties
 #  self.mask = "_{}_"
 #  self.name = name or inspect.getmodule(inspect.stack()[1][0]).__name__
 #  self.root = root or os.path.dirname(inspect.getmodule(inspect.stack()[1][0]).__file__)
 #  self.mods = self.modules()
 #  # Import Functionality
 #  self._import_ = _import_
 #  builtins.__import__ = self # weakref.ref(self, self.__del__)
 # #  print("init")
 
 def import_term(self, *args, **kvps) :
  builtins.__import__ = self._import_
 #  super(Import, self).__init__(*args, **kvps)
 #  print("term")
 
 def overlays(self, *args, **kvps) :
  return {'_module_': str(Path.cwd()/"package"/"_module_.py")}
  # Originally : return {'_module_': os.path.join(os.getcwd(),"package","_module_.py").replace("\\","\\\\")}
  
 # Start off by faking the overlays
 @patch.module("package._module_", "package/_module_.py", _mod_)
 @patch.module("package.__init__", "package/__init__.py", pkg.format(""))
 @patch.module("module",           "module.py",           mod)
 @patch("apeman.Import.modules",                          overlays)
 @patch("sys.modules", sys.modules.copy())
 class LifeSpans(unittest.TestCase) :
  """Evaluate the lifespan of an instantiated :class:`apeman.Import`."""
 
  def setUp(self):     
   """The setup function is used to store a copy of :meth:`builtins.__import__`"""
   self._import_  = builtins.__import__
 
  def tearDown(self) :
   """The tear down function is used to restore the copy of :meth:`builtins.__import__`"""
   builtins.__import__ = self._import_
 
 #  def testModule(self):
 #   from module import Class
 #   self.assertEqual(str(Class()), __name__)
 
  @unittest.skipIf(six.PY2, "patch.module untested in Python 2.7")
  def testOverlay(self):
   import package
 #   import package
 #   from module import Class
 #   self.assertEqual(str(Class()), __name__)
 #   print(str(Class()), __name__)
 
 #  @patch("apeman.Import.__del__",  import_term)
 #  @patch("apeman.Import.__init__", import_init)
 #  def testLifeSpan(self, init = None, term = None):
 #    """This tests the lifespan of a class instantiated"""
 #    if init is not None : 
 #     self.assertFalse(init.called)
 # #    else : 
 # #     print('init not patched') 
 #    if term is not None : 
 #     self.assertFalse(term.called)
 # #    else :
 # #     print('term not patched') 
 #    import module
 # #    self.assertTrue(init.called)
 # #    self.assertTrue(term.called)
 
 # @patch.module("package._module_", "package/_module_.py", _mod_)
 # @patch.module("package.__init__", "package/__init__.py", pkg.format(""))
 # @patch.module("package.__init__", "package/__init__.py", pkg.format(""))
 # @patch.module("module",           "module.py",           mod)
 # @patch("apeman.Import.modules",                         overlays)
 # @patch("sys.modules", sys.modules.copy())
 def test():
  init = set(sys.modules.keys())
  import module
  term = set(sys.modules.keys())
 #  print("test", term - init)

if __name__ == "__main__" :
#  main()
 init = set(sys.modules.keys())
 test()
 term = set(sys.modules.keys())
#  print("main", term - init)
