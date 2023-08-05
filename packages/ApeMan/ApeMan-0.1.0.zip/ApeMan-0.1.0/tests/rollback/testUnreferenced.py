"""
Unreferenced Rollback
---------------------

"""
# Todo :
#
# Test deletion with a reference
# Ensure test is reasonable as per testRollBackSansReference
# Python 2.7 Compatability
import six
# Normal Imports
import sys
import os
import builtins
# import apeman
# import gc
import unittest
if six.PY2 :
 from mock import patch
if six.PY3 :
 import overlays
# from pprint        import pprint
# import types

unreferenced = \
"""
from apeman import Import as ApeMan
ApeMan(name = '{name}', root = '{root}')
""".format(name="overlay", root = os.path.join(os.getcwd(),"overlay").replace("\\","\\\\"))
"""
The module mock up for :class:`testUnreferencedRollBack`
"""
 
if six.PY3 :
 from unittest.mock import patch
 @patch("sys.modules", sys.modules.copy()) # This protects the system modules
 class testUnreferencedRollBack(unittest.TestCase):
  """Illustrate why a reference to an instance of :class:`apeman.Import` is necessary.
  
  When :class:`apeman.Import` is instantiated it substitutes the :meth:`builtins.__import__` with itself.
  One had thought that the destructor might be used to undo this action.
  ::
  
    class ApeMan(...) :
     ...
     def __del__(self) :
      builtins.__import__ = self.imp
 
  This would allow instances of :class:`apeman.import` to be rolled back.
  
  This test shows why the delete method of :class:`apeman.Import` may not substitute :meth:`builtins.__import__` with the original method that it retains and replaces.
  When `apeman.Import` is instantiated it substitutes the :meth:`builtins.__import__` with a references to itself.
  One had thought that the destructor, :meth:`__del__`, might be used to undo this action.
  While invoking :code:`del builtins.__import__` does invoke :meth:`apeman.Import.__del__` it also wipes :meth:`builtins.__import__`, breaking the import system..
  """
  
  def setUp(self):     
   """The setup function is used to store a copy of :meth:`builtins.__import__`"""
   self._import_ = builtins.__import__
   self._modules_ = sys.modules.copy()
 #  s print("overlay" in sys.modules)
 
  def tearDown(self) :
   """The tear down function is used to restore the copy of :meth:`builtins.__import__`"""
 #   print(set(self._modules_) - set(sys.modules))
 #   old = set(dir(builtins))
   try :
    if not(hasattr(builtins, "__import__") and builtins.__import__ == self._import_) : 
     builtins.__import__ = self._import_
   except ReferenceError :  
    builtins.__import__ = self._import_
 #   new = set(dir(builtins))
 #   print(new-old)
 #   print(type(builtins.__import__))
 #   print("overlay" in sys.modules.keys())
 
  @unittest.skip("Presently builtins.__import__ is still a concrete reference to apeman.Import()")
 #  @expectedFailure("This test fails as it deletes builtins.__import__") # A problem since handled by tearDown/setUp
  @patch.module("overlay", "overlay\\__init__.py", unreferenced)                # Invokes ApeMan from an overlay
 # @patch("builtins.__import__", _import_)                                # This protects the system __import__        Note : This blocks ApeMan from swapping out __import__ for some reason and is handled within the setUp/tearDown functions as a result
  @patch("apeman.ApeMan.__del__")                                         # Tests that __del__ is called
  @unittest.skipIf(six.PY2, "patch.module untested in Python 2.7")
  def testUnreferencedDelete(self, apeman_del, _import_ = builtins.__import__) :
   # The mock, apeman_del, is used to check that the call is made during del.
   # The kvp, _import_, is necessary for the builtins.__import__ patch but this is now handled by setUp/tearDown
   """Ensure that removing :class:`apeman.Import` by :attr:`del`\ eting :meth:`builtins.__import__` does not work since :meth:`__import__` is also wiped.
 
   Without a reference to an instance of :class:`apeman.Import` one must delete :meth:`builtins.__import__`.
   This test illustrates how this might be a bad idea.
   ::
   
      from apeman import Import as ApeMan
      ApeMan()
      del builtins.__import__
  
   .. note ::
  
      If :class:`apeman.Import` is setup to behave like a Singleton i.e. it retains a reference to itself.
      Then the internal reference can interfere with the classes behaviour.
      Specifically a concrete reference prevents the class from being garbage collected while a weakref leaves the management of concrete references to the user.
      The garbage collection dictates whether or not :meth:`__del__` which in turn controls whethr or not the class is rolled back at all.
   """
 #   print([item for item in dir(builtins) if item == "__import__"])
   # Assert that the builtins.__import__ is equal to the nu/mocked _import_
   self.assertEqual(builtins.__import__, _import_)
   # Next import the overlay which invokes ApeMan as a user might
   import overlay
 #   print(overlay)
 #   try : 
   # If apeman.Import is concretely referenced then the following should execute properly
   # Assert that builtins.__import__ has infact been swapped out
 #    with self.assertRaises(AttributeError) as error : 
   self.assertNotEqual(builtins.__import__, _import_)
   # and that is is an instance of ApeMan (Specifically ApeMan is Import in this case)
 #    self.assertIsInstance(builtins.__import__, overlay.ApeMan)
   # Deleting the import method invokes Import.__del__ correctly but then wipes __import__ from builtins
   del builtins.__import__ 
   # Assert that Import.__del__ was invoked via the mock class.
   self.assertTrue(apeman_del.called)
   # Assert that builtins.__import__ is deleted, a detrimental side effect
   self.assertFalse(hasattr(builtins, "__import__"))
   # Assert that __import__ is in fact removed from the builtins module, this breaks other unittests in the module unless setUp/tearDown repair things
   with self.assertRaises(AttributeError) as error : 
    builtins.__import__ # Originally : self.assertEqual(builtins.__import__, _import_)
 #   except ReferenceError : 
 #    # If apeman.Import is weakly referenced then the following should execute properly
 #    pass  # I have no ide what to test for here, the exception is largely due to me not knowing the type for a weakref.
 #   print([item for item in dir(builtins) if item == "__import__"])
 

if __name__ == "__main__" :
 unittest.main() # This seems to call sys.exit internally
