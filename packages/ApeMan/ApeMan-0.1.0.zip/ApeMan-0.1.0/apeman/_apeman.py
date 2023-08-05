"""
Version Selection
-----------------

The file `apeman.py` does not actually do much beyond directing the interpreter to a relevant implementation.
This is simply done with the following code 
::

  if sys.version_info[:2] == (3,5) :
   from .__35__ import OverlayImporter
  if sys.version_info[:2] == (3,4) :
   from .__34__ import OverlayImporter

 
"""
# System
import os
import sys

# Debugging
from pdb import set_trace as db

# Inspection
import inspect

# Iteration
from itertools import zip_longest as zip_longest

# Imports - Why is this being done here ???
from importlib    import util, abc ,machinery

# Debugging
import logging

# Information
__version__ = "0.0.0"
modsep      = '.'

if __name__ == "__main__" :
 from pathlib import Path
 import unittest
 suite = unittest.TestLoader().discover('..')
 unittest.TextTestRunner(verbosity=1).run(suite)
#  print("Main")
#  import logging
#  logging.basicConfig(format = '%(message)s')
#  if sys.version_info[:2] == (3,4) : 
#   logger = logging.getLogger("__34__")
#  if sys.version_info[:2] == (3,5) : 
#   logger = logging.getLogger("__35__")
#  logger.setLevel(logging.DEBUG)
 
 # General Import
#  import overlay
#  from overlay import *
 # Targeted Import
#  from overlay import tiers
 # Nested Import
#  from overlay.tiers import first
 # Staggered Import
#  from overlay import tiers 
#  logger.debug("Modules     : {}\n".format([key for key in sys.modules.keys() if key.startswith('overlay') or key.startswith('tiers')]))
#  from tiers   import first
#  logger.debug("Modules     : {}\n".format([key for key in sys.modules.keys() if 'overlay' in key or 'tiers' in key]))
#  logger.debug("\n".join(["{:24} : {}".format(key, sys.modules[key]) for key in sys.modules.keys() if key.startswith('overlay') or key.startswith('tiers')]))

else :
 # Note : This code is only compatible with Python 3
 if __package__ : # Relative imports for normal usage
  if sys.version_info[:2] == (3,5) :
   print("35A")
   from .__35__ import OverlayImporter
  if sys.version_info[:2] == (3,4) :
   print("34A")
   from .__34__ import OverlayImporter
 else :           # Absolute imports prevent "SystemError : Parent module '' not loaded,..."
  if sys.version_info[:2] == (3,5) :
   print("35B")
   from __35__ import OverlayImporter
  if sys.version_info[:2] == (3,4) :
   print("34B")
   from __34__ import OverlayImporter
 
