"""
ApeMan in Python 3.4
====================

This module is considered stable within the limits allowed by
importlib in Python 3.4.

"""
# Python Compatability
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
# System
import os
import sys
# Types
import types
# Debugging
from pdb import set_trace as db
# Inspection
import inspect
# Iteration
from itertools import zip_longest as izip, tee
# Imports
from importlib    import util, abc ,machinery, _bootstrap as bootstrap
import imp
# Debugging
import logging
# Local Libraries
try :
 from . import descriptors
 from . import utilities
except SystemError:
 import descriptors
 import utilities

# Constants
modsep      = '.'

class OverlayImporter(abc.MetaPathFinder, abc.SourceLoader, utilities.Indentation):
 """
 This class combines a Finder and a Loader into an Importer. 

 .. inheritance-diagram:: apeman.__34__
    :parts: 2

 The strategy used maps overwrites the imported module with the overlay import under a different name
 Since Python imports are atomic one needs to trap modules being loaded and wrapped
 
 overlay.tiers is to be mapped to overlay._tiers_.py which 
 is imported as tiers, while tiers, the original module is
 imported as _tiers_

 .. note ::
 
  This is not an especially good implementation, it is not 
  thread safe as it does not invoke module locks when loaded.
 """
 # See section 5.5 in [1] to determine if the Path Based Finder
 # is a better fit for this class
 #
 # https://docs.python.org/3/reference/import.html
 
 root = descriptors.PathName()
 
 def __init__(self, *args, name = None, path = None, root = None, **kvps):
  super().__init__(*args, **kvps)
  self.mask = "_{}_"
  self.trap = {}
  self.wrap = {}
  self.name = name or inspect.getmodule(inspect.stack()[1][0]).__name__
  self.root = root or os.path.dirname(inspect.getmodule(inspect.stack()[1][0]).__file__)
  self.mods = self.modules()
  self.log  = logging.getLogger(__name__)
  self.log.debug("{:{}}: {:40} {}".format(self.ondent("Instance"), self.__taglen__, str(self.__class__), [key for key in sys.modules.keys() if self.name in key]))
  
 def mapToTarget(self, name) :
  """Maps request to the overlay module"""
  return modsep.join([self.mask.format(part) for part in name.split(modsep)])
  
 def modules(self) : 
  # This differs from overlays in that it recurses through the 
  # folder structure to find python modules
  ext = '.py'
  mod = lambda parts, ext : [part[:-len(ext)] if enum + 1 == len(parts) else part for enum, part in enumerate(parts)]
  lst = [(mod(file.relative_to(self.root).parts, ext), file) for file in self.root.rglob('*'+ext)]
  return {modsep.join(item[0][:-1]) if item[0][-1] == "__init__" else modsep.join(item[0]) : item[1] for item in lst}

# The 3.5 module should implement this.
#
#  def find_spec(self, name, path, target = None) :
#   self.log.debug("{}> {:<40} {:<80}".format(self.indent("FS:" + self.name),name, str(path)))
#   spec = util.spec_from_file_location(self.mapToTarget(name), str(self.modules()[self.mapToTarget(name)]))
#   self.log.debug(spec)
#   self.trap[name] = spec.loader
#   spec.loader = self
#   self.log.debug(spec)
#   return spec
#   
#  def exec_module(self, *args, **kvps) :
#   self.log.debug("Exec_Module")
#   self.log.debug(args)
#   self.log.debug(kvps)
#  
#  def create_module(self, *args, **kvps) :
#   self.log.debug("Create_Module")
#   self.log.debug(args)
#   self.log.debug(kvps)
  
 
 def find_module(self, name, path=None):
#   self.log.debug("Find_module")
  self.log.debug("{}> {:<40} {:<80}".format(self.indent("F:" + self.name),name, str(path)))
#   self.log.debug([sys.modules[key] for key in sys.modules.keys() if name in key])
  if self.mapToTarget(name) in self.mods :                    # User imports _PACKAGE_
#    self.log.debug(self.undent("F:Trap"))
   self.trap[name] = self.mods.pop(self.mapToTarget(name))
   return self
  if self.trap.pop(name) :                                    # overlay imports PACKAGE
#    self.log.debug(self.undent("F:Wrap"))
   for meta in [meta for meta in sys.meta_path if meta is not self]:
    self.wrap[name] = self.wrap.get(name) or meta.find_module(name, path)
   return self
#   if name in self.wrap :                                      # overlay imports PACKAGE
#    return self
  return None
 
 def load_module(self, name):
#   self.log.debug("{}: {:<40}".format(self.indent("L:" + self.name),name))
  load = sys.modules.get(name)
  if name in self.trap :
   # One should strictly use SourceFileLoader here instead.
#    self.log.debug(self.ondent("L:Trap"))
   file = self.trap.get(name)
   load = types.ModuleType(self.mapToTarget(name))
   with file.open('r') as data : code = data.read()
#    self.log.debug([key for key in sys.modules.keys() if name in key])
   load.__file__ = str(file)
   code = compile(code, str(file), 'exec')
   sys.modules[name] = load # must occur before exec
   exec(code, load.__dict__)
#    self.log.debug([key for key in sys.modules.keys() if name in key])
#    self.log.debug(load.__version__)
  if name in self.wrap :
   # Note : importing PACKAGE as _PACKAGE_ fails. 
   # This is due to the to the `builtin` importers preventing
   # name changes. To be explicit they can't find a funny 
   # named module and one can't cross assign the module. One
   # can reassign it however
#    self.log.debug(self.ondent("L:Wrap"))
   spec = self.wrap.pop(name)
   load = spec.load_module()
#   self.log.debug([sys.modules[key] for key in sys.modules.keys() if name in key])
#   self.log.debug(self.undent("L:Done"))
  return load
  
#   temp = self.modules()
#   file = str(temp[self.mapToTarget(name)])
#   self.log.debug([key for key in sys.modules.keys() if name in key])
#   OverlayLoader(self.mapToTarget(name), file).load_module(self.mapToTarget(name))
#   self.log.debug([key for key in sys.modules.keys() if name in key])
#   OverlayLoader(name, file).load_module(self.mapToTarget(name))
#   self.log.debug([key for key in sys.modules.keys() if name in key])

#   self.log.debug(self.mapToTarget(name))
#   self.log.debug(self.modules().keys())
#   file = self.modules()[self.mapToTarget(name)]
# #   self.log.debug(file)
#   temp = machinery.SourceFileLoader(name, [str(self.root)])
#   temp.load_module()
#   temp = machinery.SourceFileLoader(name, self.modules()[self.mapToTarget(name)]).load_module() # be weary here, re-assigning names is a bit finnicky and has a rollover impact.
#   sys.modules[name] = temp # Using sys.modules[module] = temp fails
#   self.log.debug([key for key in sys.modules.keys() if key in name])
#   self.trap[name].load_module()
#   temp = OverlayLoader(name, str(self.trap[name])).load_module(modsep.join([self.name,name]))
#   temp = machinery.SourceFileLoader(name, str(self.trap[name])).load_module()
#   return temp
#   self.log.debug([key for key in sys.modules.keys() if key in name])

#    # be weary here, re-assigning names is a bit finnicky and has a rollover impact.
#   sys.modules[name] = temp # Using sys.modules[module] = temp fails
#   parent, _, module = name.partition(modsep) # Was rpartition
#   if name in self.trap : # This might break
#    # Handle Source Import
#    self.trap.pop(name)
#    self.log.debug(self.ondent("Pass Trapped"))
#    temp = self.temp.load_module()
#    sys.modules[self.mapTarget(name)] = temp
#    self.log.debug("{}< {}".format(self.undent("Imported"),self.mapTarget(name)))
#    return temp
#   else :
#    # Handle Overlay Import
#    if module in sys.modules:           # Already Imported
#     return sys.modules[module]         # Modules' absolute path
#    # Import the module
#    self.trap.append(module)
#    file = self.mapToRoot(name)
#    _name_ = self.mapToSource(name)
#    root,stem = self.pathParts(self.mapToSource(name))
#    self.log.debug("{}: {:18} -> {:18} {:80}".format(self.ondent("FileLoader"),root, stem, file))
#    temp = machinery.SourceFileLoader(name, file).load_module() # be weary here, re-assigning names is a bit finnicky and has a rollover impact.
#    sys.modules[name] = temp # Using sys.modules[module] = temp fails
#    self.log.debug("{}< {}".format(self.undent("Imported"),temp))
#    return temp

if __name__ == "__main__" :
 # Setup Logging
 import logging
 logging.basicConfig(format = '%(message)s')
 logger = logging.getLogger() # "__34__"
 logger.setLevel(logging.DEBUG)
 
 # Call Test Suites
#  import unittest
#  tests = {
#   "all"      : 'test*.py',
#   "overlay"  : '*Overlay.py',
#   "uppercase": '*UpperCase.py',
#   "tiers"    : '*Tiers.py',
#  }
#  test = 'all'
#  suite = unittest.TestLoader().discover('..',tests[test])
#  unittest.TextTestRunner(verbosity=1).run(suite)

 __root__ = os.path.join(os.path.dirname(os.path.abspath(__file__)),'..\\tests')

 sys.path.append(__root__)

 import builtins
 def _import_(*args, importer = __import__) :
  # Hooks the import statement
  logger.debug("import : {}".format(args[0]))
  temp = importer(*args)  
#   logger.debug(dir(temp))
  logger.debug([temp.__name__, temp.__file__, temp.__package__, temp.__loader__])
  return temp
 
 # Atomic Imports
 import uppercase
 builtins.__import__ = _import_ 
#  logger.debug([sys.modules[key] for key in sys.modules.keys() if 'tiers' in key])
#  logger.debug("Primary")
#  import tiers
#  logger.debug([sys.modules[key] for key in sys.modules.keys() if 'tiers' in key])
#  logger.debug(tiers.__version__)
 logger.debug("Secondary")
 from tiers import module_a
#  logger.debug([sys.modules[key] for key in sys.modules.keys() if 'tiers' in key])
#  logger.debug([sys.modules[key] for key in sys.modules.keys() if 'os' in key])
#  logger.debug(module_a.__version__)
#  from tiers import package_a
#  logger.debug([sys.modules[key] for key in sys.modules.keys() if 'tiers' in key])
#  logger.debug([sys.modules[key] for key in sys.modules.keys() if 'os' in key])
 logger.debug(package_a.__version__)
 
 # Implicit Root Import
#  from overlay import * # Test with/out __all__ defined
 # Explicit Root Import
#  from uppercase import tiers
 # Explicit Nested import
#  from overlay.tiers import module_a
 # Explicit Nested import
#  from overlay.tiers.module_a import Alpha
#  print(Alpha())
 # Explicit Staged import
#  from overlay import tiers 
#  logger.debug("Modules     : {}\n".format([key for key in sys.modules.keys() if key.startswith('overlay') or key.startswith('tiers')]))
#  from tiers   import module_a
#  logger.debug("Modules     : {}\n".format([key for key in sys.modules.keys() if 'overlay' in key or 'tiers' in key]))
#  logger.debug("\n".join(["{} : {}".format(key, sys.modules[key]) for key in sys.modules.keys() if key.startswith('overlay') or key.startswith('tiers')]))
