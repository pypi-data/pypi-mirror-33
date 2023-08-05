"""
===================
Python 3.5 : ApeMan
===================

"""
# Python Compatability
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
# Flags
DEBUG = True
# System
import os
import sys
import builtins
# Debugging
if DEBUG : from pdb import set_trace as db
# Inspection
import inspect
# Iteration
from itertools import zip_longest as izip, tee
# Imports
from importlib    import util, abc, machinery, _bootstrap as bootstrap, import_module
import imp
# Local Libraries
try :
 from .descriptors import PathName
 from .utilities   import Indentation
except (SystemError) :
 from descriptors  import PathName
 from utilities    import Indentation
# Logging
if DEBUG : import logging

# Constants
modsep      = '.'
version     = (0,0,0)

class Import(Indentation):
 # This comes from the Python 3.6 implementation which ultimately comes from the 3.4 implementation
 """
 This class replaces the `builtins.import` function with itself.
 Bypassing the ModuleSpec and Finder/Loader or Importer mechanisms.
 
 .. note :: This class fails to work properly

 .. note :: This is derived from the Python 3.4 implementation.
 """
 
 root = PathName()
 lom = []
 _import_ = builtins.__import__

 def __init__(self, *args, name = None, path = None, root = None, _import_ = __import__, debug = DEBUG, **kvps):
  super().__init__(*args, **kvps)
  # Properties
  self.mask = "_{}_"
  self.name = name or inspect.getmodule(inspect.stack()[1][0]).__name__
  self.root = root or os.path.dirname(inspect.getmodule(inspect.stack()[1][0]).__file__)
  self.mods = self.modules()
#   print(self.mods)
  # Logging and Debugging
  self.debug = debug
  if self.debug : self.log  = logging.getLogger(__name__)
  if self.debug : self.log.debug("Initialized : Import")
#   if self.debug : self.log.debug("{:{}}: {:40} {}".format(self.ondent("Instance"), self.__taglen__, str(self.__class__), [key for key in sys.modules.keys() if self.name in key]))
#   if self.debug : self.log.debug("{:10}: {:40} {}".format(self.ondent("Instance"), str(self.__class__), [key for key in sys.modules.keys() if self.name in key]))
  if self.debug : self.log.debug("Modules     : {}".format(sorted(self.mods.keys())))
  # Import Functionality
  self._import_ = _import_
  builtins.__import__ = self

 def __call__(self, name, *args, **kvps) : # (self, *args, *kvps):  
  # Hooks the import statement
#   self.log.debug([{arg['__name__']:arg.keys()} if isinstance(arg, dict) else arg for arg in args])
  if self.mapToTarget(name) in self.mods.keys() :
#    if self.debug : self.log.debug("Overloading : {}".format(name))
   self.log.debug(self.lom)
   if name in self.lom :
    if self.debug : self.log.debug("Reverting   : " + name)
    return self._import_(name, *args, **kvps)
#    self.log.debug("remap : " + name + " -> "+ self.name + "." +self.mapToTarget(name))
#    self.log.debug(name)
#    self.log.debug(self.name + modsep + self.mapToTarget(name))
#    self.log.debug("Wrapped Import")
   self.lom.append(name)
   if self.debug : self.log.debug("Redirecting : {}".format(self.name + modsep + self.mapToTarget(name)))
   return import_module(self.name + modsep + self.mapToTarget(name)) # This is a little black magic as we ignore the args
  if self.debug : self.log.debug("Importing   : {}".format(name))
  return self._import_(name, *args, **kvps)

 def mapToTarget(self, name) :
  """Maps request to the overlay module"""
  # Converts tiers.package.module to _tiers_._package_._module_
  return modsep.join([self.mask.format(part) for part in name.split(modsep)])

 def modules(self) : 
  """Lists the overlays implemented within a directory"""
  # This differs from overlays in that it recurses through the 
  # folder structure to find python modules
  ext = '.py'
  mod = lambda parts, ext : [part[:-len(ext)] if enum + 1 == len(parts) else part for enum, part in enumerate(parts)]
  lst = [(mod(file.relative_to(self.root).parts, ext), file) for file in self.root.rglob('*'+ext)]
  return {modsep.join(item[0][:-1]) if item[0][-1] == "__init__" else modsep.join(item[0]) : item[1] for item in lst}

class OverlayLoader(machinery.SourceFileLoader) :
 """
 .. note ::

    This was deliberately named OverlayLoader, verify that this is still true.
 """
 #  Reference [1] is essentially useless but gives an example
 #  [1] http://stackoverflow.com/a/29585082/958580

 flag = True
 
 def __init__(self, *args, logger = logging.getLogger(__name__), debug = DEBUG, **kvps):
  super().__init__(*args, **kvps)
  if self.debug : self.log  = logging.getLogger(__name__)
  
 def create_module(self, spec, *args, **kvps) :
#    temp = super().create_module(spec, *args, **kvps)
  if self.flag:
   self.flag = False
   if self.debug : self.log.debug("\n".join(dir(util)))
#     self.log.debug("\n".join(dir(spec)))
#    temp = util.module_from_spec(spec) # Python 3.5
   temp = spec.loader.load_module()
   if self.debug : self.log.debug(temp)
   return temp
  return None 
  
class OverlayImporter(abc.MetaPathFinder) :
 # This is not a True importer according to the python doc's 
 # This is because it does not fomerly find and load a module.
 # This is due to the fact that the machinery.*Loader classes
 # expect a name and a path when instantiated. While this has 
 # to accomodate it's own state.
 
 # ref : 1                          find_spec and mapToSystem
 # 
 # Here we defer the spec search to the import machinery and 
 # modify the result somewhat.
 #
 # ref : 2                          find_spec and mapToSystem
 #
 # One may generate a module spec using the ModuleSpec method
 # and a folder name as an argument to SourceFileLoader but 
 # this clashes saying there is a permission error for some
 # reason
 #
 # ref : 3                          find_spec and mapToSystem
 #
 # One must generate a spec by either importing a moule or an
 # __init__.py file or one must and use a file Loader
 # 

 # Logging
 dent = 0
 def indent(self, label = None, char = " ", length = 10):
  self.dent += 1
  return "{0}{1:{2}}".format(char*self.dent, label[:length-self.dent],length-self.dent)

 def undent(self, label = None, char = " ", length = 10):
  self.dent -= 1
  return "{0}{1:{2}}".format(char*self.dent, label[:length-self.dent],length-self.dent)

 def ondent(self, label = None, char = ".", length = 10):
  return "{0}{1:{2}}".format(char*self.dent, label[:length-self.dent],length-self.dent)

 # Mapping
 def mapToSource(self,name) :
  """Maps request to the corresponding overlay module"""
  # Consider the use of util.resolve_name(name, path)
  return modsep.join([part if test else self.mask.format(part) for test, part in izip(self.name.split(modsep),name.split(modsep))])

 def mapToTarget(self, name) :
  return modsep.join([part for test, part in izip(self.name.split(modsep),name.split(modsep)) if not test])
#    return modsep.join(name.split(modsep)[1:])
  
 def mapToHidden(self,name) :
  """Maps request to a corresponding hidden module"""
#    for trap in self.trap :
#     parts = trap.split(modsep)
  return modsep.join([self.mask.format(part) for part in name.split(modsep)])

 def mapToSystem(self, name):
  """Maps a module to the corresponding overlay system path"""
  # This finds the first folder or file matching the module name
  # note that name must be processed beforehand using self,mapToSource
  stem = [part for test, part in izip(self.name.split(modsep),name.split(modsep)) if not test]
  test, item = tee(os.path.join(path, *stem) for path in self.path)
  path = None
  while next(test, None) : 
   path = next(item, None)
   if not os.path.isdir(path) :              # [ref:2]
    path += '.py'     
  return path

 def mapToFile(self, name, path):
  """ Similar to mapToSystem but for packages it tries to map to __init__.py files"""
  # Note one must premap the path FQMN using mapToSource
#    self.log.debug("MapToFile : {}".format(self.path))
  stem = [part for test, part in izip(self.name.split(modsep),name.split(modsep)) if not test]
  test, item = tee(os.path.join(path, *stem) for path in path)
  path = None
  while next(test, None) : 
   path = next(item, None)
#     self.log.debug(path)
   if os.path.isdir(path) :                  # [ref:3]
    path = os.path.join(path, '__init__.py') 
   else :                                    
    path += '.py'     
  return path

#   def modules():
#    return [os.path.splitext(item)[0] for item in os.listdir(self.path[0]) if os.path.splitext(item)[0] not in ["__init__","__pycache__"]]

 # Importer Code
 trap = []
 
 def __init__(self, *args, path = None, name = None, logger = logging.getLogger(__name__), debug = DEBUG, **kvps):
  # The following alternate call structure may be necessary 
  #
  # __init__(self, path, *args, logger = logging.getLogger(__name__), **kvps)
  #
  # Where path maps the values roughly as follows :
  #
  #  name = name or inspect.getmodule(inspect.stack()[1][0]).__name__
  #  path = name or inspect.getmodule(inspect.stack()[1][0]).__path__
  #
#    logger.debug("Args : {} \nKvps :".format(args, kvps))
  super().__init__(*args, **kvps)
  self.mask = "_{}_"
#    db()
  self.name = name or inspect.getmodule(inspect.stack()[1][0]).__name__
  self.path = path or inspect.getmodule(inspect.stack()[1][0]).__path__
  self.debug = debug
  if self.debug : self.log  = logging.getLogger(__name__)
  if self.debug : self.log.debug("Initialized : {:74} {}".format(self.name, self.path))
  sys.meta_path.insert(0, self)
#   if self.debug : self.log.debug("{}".format(sys.meta_path))

 def find_spec(self, name, path, target = None): # This is a class method within importlib
  # path is the absolute import path while name may be a relative
  # 
  # Note it's useful to use either 
  #
  # spec_from_file_location
  # spec_from_loader
  #
  # Target is only specified if thisi is a re-import
#    if 'overlay' not in name or "tiers" not in name :
#     return None
  if self.debug : self.log.debug("find_spec   : {1:24} {0:24} {3:24} {2}".format("({})".format(self.name), name, path, str(target)))
  if name.startswith(self.name) and name not in self.trap :
   _trap_ = self.mapToTarget(name)
   _name_ = self.mapToSource(name)
   _path_ = self.mapToFile(_name_, path)
   if self.debug : self.log.debug("Overlay     : {1:24} {0:24} {3:24} {2}".format("({})".format(self.name), _name_, _path_, _trap_))
   if _trap_ : # The following should always execute and the error shoulf never be raised
    self.trap.append(_trap_) 
   else : 
    raise ValueError("The name {} could not be mapped to {}. ".format(name, _trap_))
#     self.log.debug("              {:50}-> {:50}\n             {:50} -> {:50} ".format(name, _name_, str(path), _path_))
#     self.log.debug(self.mapToSystem(_name_))
#     spec = util.find_spec(self.mapToSource(name), path)                                           # [ref:1]
#     spec.name = _name_
#     self.log.debug(spec)
#     self.log.debug([attr for attr in dir(spec.loader) if not attr.startswith('__')])
#     self.log.debug(spec.loader.path)
#     loader = machinery.SourceFileLoader(name, _path_)                                             # [ref:2]
#     spec = util.spec_from_loader(name, loader)
#     self.log.debug(loader.path)
#     self.log.debug(loader)
#     spec = machinery.ModuleSpec(
#      name     = _name_, 
#      loader   = loader,
#      origin = _path_,
# #      submodule_search_locations = _path_,
#      is_package=True,
#      )
#     self.log.debug(spec)
   spec = util.spec_from_file_location(name, _path_, loader = OverlayLoader(name, _path_))                         # [ref:3]
    # spec_from_file asscepts the following arguments 
    #  name                      - One may alter this
    #  location                  - The location of the package, that is a file path, or "NameSpace"
    #  loader                    - The loader that the package must use  (Note this is picked for use if one is not provided)
    #  submodule_search_location - The submodule locations in the system (Note this is picked for use if one is not provided)
#     self.log.debug("Module Spec.: {}".format(spec))
#     spec = util.find_spec(_name_, path)
#     self.log.debug(spec)
#     util.spec_from_loader(name, spec.loader)
#     self.log.debug(spec)
   return spec
  if self.debug : self.log.debug("Should Trap : {} in {} as {}".format(name, self.trap, self.mapToHidden(name)))
#    if name in self.trap :
#     self.log.debug("Trapped     : {1:24} {0:24} {3:24} {2}".format("({})".format(self.name), name, path, " ".join(self.trap)))
#     self.trap.pop(self.trap.index(name))
#     spec = util.find_spec(name, path)
# #     self.log.debug("\n".join(dir(spec)))
# #     self.log.debug(util.spec_from_loader(name, spec.loader, origin = spec.origin, is_package =True))
# #     self.log.debug(machinery.ModuleSpec(name, spec.loader, origin = spec.origin, loader_state = spec.loader_state))
#     spec.name = self.mapToHidden(spec.name)
# #     spec.submodule_search_locations.append(self.)
# #     self.log.debug("\n".join(dir(spec.submodule_search_locations))) # shows the append method is accessible
#     self.log.debug(spec)
#     return spec
  return None

#   def find_spec(self, name, path, target = None):  
#    self.log.debug("{0}:{1:20} {3} \n {2}".format(self.ondent("find_spec"), name, "\n ".join(path) if isinstance(path, list) else path, target))# self.ondent("FindSpec"), name, path, target))
#    return super().find_spec(name, path, target)

#   def loader():
#    # Use module_from_spec here (Python 3.5 onwards)
#    # Use loader.load_module    (Python 3.4)

if __name__ == "__main__" :
#  print("Main")
# import logging
# logging.basicConfig(format = '%(message)s')
# logger = logging.getLogger("__35__")
# logger.setLevel(logging.DEBUG)

 # Call Test Suites
 import unittest
 tests = {
  "all"        : 'test*.py',
  "overlay"    : '*Overlay.py',
  "assumptions": '*Assumptions.py',
  "machinery"  : '*Machinery.py',
  "scaffold"   : '*Scaffoled.py',
  "structure"  : '*Structure.py'}
 test = 'structure'
 suite = unittest.TestLoader().discover('..',tests[test])
 unittest.TextTestRunner(verbosity=1).run(suite)

# 760 GB ~ 20 Million Pages

 # General Import
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
 # Log message
#  logger.debug("\n".join(["{:24} : {}".format(key, sys.modules[key]) for key in sys.modules.keys() if key.startswith('overlay') or key.startswith('tiers')]))
