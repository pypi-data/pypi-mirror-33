"""
Repetition
==========

These tests ensures that repeatedly importing the same module returns the same module from the overlay and not the original module.
That is any import when an overlay is in effect consistently pulls in the same patch.

This is the reason the scope is checked within ApeMan to ascertain wheterh of not the patch is importing the original module or if some module is importing the patch.
This same switch might prevent the end user from using multiple overlays that patch the same module.
If this is the case then it may become necessary for all overlays to share the modules they patch and which modules are being imported at a given time.

"""
import six
import os
import sys
import builtins
# from path import pathlib
if six.PY3:
 import overlays
 from unittest      import TestCase, main
 from unittest.mock import patch

overlay = """
from apeman import ApeMan 
apeman = ApeMan(name="{name}",root="{root}")
""".format(name = "overlay", root = os.path.join(os.getcwd(),"overlay").replace("\\","\\\\"))

_module_ = """
from math import *
# from math import pi
pi = 3*pi
"""

# #format() # math seems easiest to overlay versus say fnmatch/glob/re
if six.PY3 : 

 def echo(data):
  return lambda *args, **kvps : data

 @patch("sys.modules", sys.modules.copy())
 class testRepeats(TestCase) :
  """
  The intention here is to test patched modules that are imported more then once.
  ::
  
    import overlay
    import os
    import os
  
  Similarly testing repeated imports performed within different scopes must be done
  ::
  
    import overlay
    import os
    def|class SCOPE() :
     import os
  
  It is also necessary to ensure that imports made from different modules import the same module.
  This last requirement is quite fundamental to stable operation of ones code across imports.
  """
  def setUp(self) :
   """Protect builtins.__import__"""
#    from math import pi
#    self.pi = 2 * pi
#    self._import_ = builtins.__import__
  
  def tearDown(self) :
   """Restore builtins.__import__"""
#    builtins.__import__ = self._import_
 
# #   @patch.module("overlay",        "overlay/__init__.py", overlay)
# #   @patch.module("overlay._math_", "overlay/_math_.py",   overlay_math)
#   @patch.module("overlay",        "overlay",   overlay_math)
#   @patch("apeman.Import.modules", echo({"_math_":"overlay/_math_.py"}))
#  #  @patch("apeman.ApeMan.__del__")                                         # Tests that __del__ is called
#   # This must also patch the ApeMan has modules 
#   def testRepeatsWithinSameScope(self) :
#    """Test repeated impots performed within the same scope
#    ::
# 
#      import overlay
#      import os
#      import os
#    """
#    import overlay
#  #   from math import pi
#  #   answer = pi
#  #   from math import pi
#  #   result = pi
#  #   self.assertEqual(answer, result)
#  #   print((answer, result,self.pi))
   
  @patch.module("overlay._math_", "overlay/_math_.py", _module_)
  @patch.module("overlay",        "overlay",           overlay)
  @patch("apeman.Import.modules", echo({"_math_":"overlay/_math_.py"}))
  # This must also patch the ApeMan has modules 
  def testRepeatsWithinSameScope(self) :
   """"""
   import overlay
   import math
   print(math.pi)
#    from math import pi
#    print(pi)

if __name__ == "__main__":
 init = sys.modules
 main()
 term = sys.modules
 print(init-term)