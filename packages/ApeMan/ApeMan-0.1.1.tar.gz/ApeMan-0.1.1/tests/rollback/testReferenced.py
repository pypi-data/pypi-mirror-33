"""
Referenced Rollback
-------------------

"""
# Todo :
#
# Test deletion with a reference
# Ensure test is reasonable as per testRollBackSansReference
# Python 2 Compatability
import six
# Normal imports
import sys
import os
import builtins
# import apeman
# import gc
import unittest
if six.PY2 :
#  import unittest2 as unittest
 from mock import patch
if six.PY3:
 import overlays 
# Here we save a reference to the builtin import method.
# IMPORT = builtins.__import__

# def verbose(*args, **kvps) :
#  print("Importing",args, kvps)
#  return IMPORT(*args, **kvps)
# builtins.__import__ = verbose

# def duplicate(fxn, name = None) :
#  try :
#   return types.FunctionType(fxn.__code__, fxn.__globals__, name or fxn.__name__, fxn.__defaults__, fxn.__closure__)
#  except AttributeError : # Fails when fxn is a builtin
#   def fun(*args, **kvps):
#    """Built In Function"""
#    return fxn(*args, **kvps)
#   return fun 

# def _import_(*args, **kvps) :
#  """
#  This is a wrapper around builtins.__import__ used for testing
#  """
#  return IMPORT(*args, **kvps)

referenced = \
"""
from apeman import Import as ApeMan
apeman = ApeMan(name = '{name}', root = '{root}')
""".format(name="overlay", root = os.path.join(os.getcwd(),"overlay").replace("\\","\\\\"))
"""
The module mock up for :class:`testReferencedRollBack`
"""

if six.PY3 :
#  import unittest
 from unittest.mock import patch
# from pprint        import pprint
# import types
 @patch("sys.modules", sys.modules.copy()) # This protects the system modules
 # @patch("builtins.__import__")             # This is handled by the setUp/tearDown methods instead.
 class testReferencedRollBack(unittest.TestCase):
  """
  This test ensures that a user retains a reference to :class:`apeman.Import`.
  Not doing so causes the instance to be garbage collected, breaking the import mechanism.
  """
 
  def setUp(self):     
   """The setup function is used to store a copy of :meth:`builtins.__import__`"""
   self._import_  = builtins.__import__
 #   self._modules_ = sys.modules.copy()
 #   print("overlay" in sys.modules)
 
  def tearDown(self) :
   """The tear down function is used to restore the copy of :meth:`builtins.__import__`"""
 #   old = set(dir(builtins))
 #   if not(hasattr(builtins, "__import__") and builtins.__import__ == self._import_) : 
   builtins.__import__ = self._import_
 #   new = set(dir(builtins))
 #   print(new-old)
 #   print(set(self._modules_) - set(sys.modules))
 #   print(type(builtins.__import__))
 #   print("overlay" in sys.modules.keys())
 
  @unittest.skip("Presently builtins.__import__ is still a concrete reference to apeman.Import()")
  @patch.module("overlay", "overlay\\__init__.py", referenced)                    # Invokes ApeMan from an overlay
 #  @patch("apeman.Import.__del__")                                         # Tests that __del__ is called
  @unittest.skipIf(six.PY2, "patch.module untested in Python 2.7")
  def testReferencedDelete(self, _import_ = builtins.__import__) :
   """Ensure :class:`apeman.Import` may be deleted given a reference to it's instance. 
   
   The test asserts that the following code succeeds
   ::
   
     from apeman import Import as ApeMan
     apeman = ApeMan()
     del apeman
 
   .. note ::
   
      This test fails if :class:`apeman.Import` creates a concrete reference to itself through :meth:`builtins.__import__`.
      A concrete reference causes the class to persist and not be deleted.
      This is also the reason that care must be taken converting :class:`apeman.Import` into a singleton.
   """
   # Assert that the builtins.__import__ is equal to the nu/mocked _import_
   self.assertEqual(builtins.__import__, _import_)
   # Next import the overlay which invokes ApeMan as a user might
   import overlay
 #   print(overlay)
   # Assert that builtins.__import__ has in fact been swapped out
   self.assertEqual(overlay.apeman._import_, _import_)   # If we had mocked builtins.__import__ then this fails since imports through apeman.imp generate new mocks from the original mock for _import_ 
 #   self.assertEqual(overlay.apeman, builtins.__import__) # This fails if builtins.__import__ is a weakref
   # and that it is an instance of apeman.Import
 #   self.assertIsInstance(builtins.__import__, overlay.ApeMan) # This fails if builtins.__import__ is a weakref
   # Deleting the import method invokes Import.__del__ correctly but then wipes __import__ from builtins
   del overlay.apeman
   # Other mechanisms by which __import__ may be replaced
 #   builtins.__import__.__del__()
 #   overlay.apeman.__del__()
 #   delattr(overlay,"apeman")
 #   del builtins.__import__ overlay.apeman
 #   gc.collect()
   # Assert that Import.__del__ was invoked via the mock class
   self.assertNotIsInstance(builtins.__import__, overlay.ApeMan)
 #   self.assertEqual(builtins.__import__, _import_)
 
if __name__ == "__main__" :
 unittest.main()