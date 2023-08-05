"""
===================
Python 3.3 : ApeMan
===================

"""
# Python Compatability
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
# System
import os
import sys
from pathlib import Path
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
# Descriptors
from .descriptors import FileName, PathName, RootName
# Utilities
from .utilities import Indentation, sliceLists as stack

# Constants
modsep      = '.'
version     = (0,0,0)

class OverlayFinder(object) :
#  set_data        = SourceFileLoader.set_data
#  _cache_bytecode = SourceFileLoader._cache_bytecode
 pass  

# class OverlayLoader(external.SourceLoader) :
# #  set_data        = SourceFileLoader.set_data
# #  _cache_bytecode = SourceFileLoader._cache_bytecode
#  __init__     = external.FileLoader.__init__
#  __eq__       = external.FileLoader.__eq__
#  __hash__     = external.FileLoader.__hash__
#  load_module  = external.FileLoader.load_module
#  get_filename = external.FileLoader.get_filename
#  get_Data     = external.FileLoader.get_data

# class OverlayLoader(machinery.SourceFileLoader):
#  def __init__(self, *args, **kvps):
#   super().__init__(*args, **kvps)
#   self.log  = logging.getLogger(__name__)
  
#  def load_module(self, name, *args, **kvps):
#   # Supposedly overwriting this method, in a subclass, should 
#   # void the @_name_check decorator active upon the method
#   try : 
#    super(OverlayLoader, self).load_module(name, *args, **kvps)
#   except ImportError as er : 
#    self.log.debug(sys.modules)
#    temp = bootstrap._load_module_shim(self, name)
#    self.log.debug(sys.modules)
#    return temp

class OverlayImporter(abc.MetaPathFinder, abc.Loader):
 # This class combines a Finder and a Loader into a unified Importer.
 #
 # FQMN - Fuly Qualified Module name                 overlay.tiers                  This is what the user imports i.e. the handler or wrapper
 #
 # FQON - Fuly Qualified Overlay name                tiers                          This is what is installed i.e. the overlay
 # FQAN - Fuly Qualified Hidden/Abstracted name      _tiers_                        This is what should have been installed but is now covered up i.e. the original
 #
 #*FQSN - Fuly Qualified System name                 overlay._tiers_                This is what the user really imports
 #
 # FQPN - Fuly Qualified Path name                   overlay\\tiers                 This is the relative path name
 # FQFN - Fuly Qualified Path name                   overlay\\tiers\\.__init__.py   This is the relative file name (e.g. for a File rather then a Path loader)
 #
 # * This entry is probably redundant or meant to be deprecated
 #
 # The strategy here is to map an import under a different name
 # Since Python imports are atomic one needs to trap modules being loaded and wrapped
 #
 # overlay.tiers is to be mapped to overlay._tiers_.py which 
 # is imported as tiers, while tiers, the original module is
 # imported as _tiers_
 #
 
 # Indentation Constants
 __indent__ = 0
 __taglen__ = 18

 # Main Class Implementation
 root = PathName()
 
 def __init__(self, *args, name = None, path = None, root = None, **kvps):
  super().__init__(*args, **kvps)
  self.mask = "_{}_"
  self.trap = {}
  self.mods = self.modules()
  self.name = name or inspect.getmodule(inspect.stack()[1][0]).__name__
  self.root = root or os.path.dirname(inspect.getmodule(inspect.stack()[1][0]).__file__)
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
  self.log.debug("{}> {:<40} {:<80}".format(self.indent("F:" + self.name),name, str(path)))
  # Overlay Layer
  temp = self.mods.get(self.mapToTarget(name))
  if temp :
   if name in self.trap : 
    # overlay imports PACKAGE
    self.log.debug(self.ondent("Wrap"))
    for meta in [meta for meta in sys.meta_path if meta is not self]:
     self.wrap[name] = self.wrap.get(name) or meta.find_module(name, path)
    return self
   else :
    # User imports _PACKAGE_
    self.log.debug(self.ondent("Trap"))
    self.trap[name] = temp
    return self
  return None 
 
 def load_module(self, name):
  self.log.debug("{}: {:<40}".format(self.indent("L:" + self.name),name))
  load = sys.modules.get(name)
  if load is None :
   if name in self.wrap :
    # Note : importing PACKAGE as _PACKAGE_ fails. 
    # This is due to the to the built in importers preventing
    # name changes. To be explicit they can't find a funny 
    # named module and one can't cross assign the module. One
    # can reassign it however
    module      = self.wrap[name]
    load = module.load_module()
   if name in self.trap :
    file = self.modules()[self.mapToTarget(name)]
    load = types.ModuleType(self.mapToTarget(name))
    with file.open('r') as data : code = data.read()
    self.log.debug([key for key in sys.modules.keys() if name in key])
    load.__file__ = str(file)
    code = compile(code, str(file), 'exec')
    exec(code, load.__dict__)
    sys.modules[name] = load
    self.log.debug([key for key in sys.modules.keys() if name in key])
    self.log.debug(load.__version__)
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

 # Atomic Imports
 import uppercase
#  print([key for key in sys.modules.keys() if 'tiers' in key])
 import tiers
 import tiers
#  print([key for key in sys.modules.keys() if 'tiers' in key])
 print(tiers.__version__)
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
