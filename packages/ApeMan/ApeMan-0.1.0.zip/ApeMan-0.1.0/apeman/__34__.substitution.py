"""

Local vs. Global 
================

One may instantiate the OverlayImporter class at each level in
the structure or at the root. The first case requires that the
importer be installed at each tier, the latter requires it's 
installation at the root of the overlay. 

Installation at each tier requires a method to know how far the
nesting of that tier module goes. That is from an __init__.py
there does not seem to be a clean means of travering the hier-
archy to find the FQMN for the file.

For this reason and for end users implementation purposes the 
The OverlayImporter must be installed within the package root
and all imports are done relative to that location. e.g. 

 overlay/
  __init__.py
  package_a/
   package_b/
    package_c/
     module_d
     
In theory it also makes it possible to fiddle with name space
packages in some ways.

"""
# Python Compatability
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
# System
import os
import sys
# Debugging
from pdb import set_trace as db
# Inspection
import inspect
# Iteration
from itertools import zip_longest as izip, tee
# Imports
from importlib    import util, abc ,machinery
import imp
# Debugging
import logging

# Constants
modsep      = '.'
 
# def outer(name):
#   frame = inspect.stack()[1][0]
#   while name not in frame.f_locals:
#     frame = frame.f_back
#     if frame is None:
#       return None
#   return frame.f_locals[name]

class OverlayImporter(abc.MetaPathFinder, abc.Loader):
 # PEP302 prescribes the use of two different classes, a Finder 
 # and a Loader, that find and load modules respectively. Each 
 # respectively provides a find_module and a load_module method.
 # These two classes can be combined into a unified Importer.
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
 #
 # Given the following module to import 
 #
 # overlay.tiers is to be mapped to overlay._tiers_.py which 
 # is imported as tiers, while tiers, the original module is
 # imported as _tiers_
 #
 
# if __debug__ :
 # When Branching this into it's own class call it DebugLabels
 # This should be a standalone mixin, that is one should resist
 # the temptation to mixin logging.
 __indent__ = 0
 __taglen__ = 18

 def indent(self, label = None, char = " ", length = __taglen__):
  if label :
   message = "{0}{1:{2}}".format(char*self.__indent__, label[:length-self.__indent__], max(length-self.__indent__,1))
  else :
   message = ""
  self.__indent__ += 1
  return message

 def undent(self, label = None, char = " ", length = __taglen__):
  if label :
   message = "{0}{1:{2}}".format(char*self.__indent__, label[:length-self.__indent__],length-self.__indent__)
  else :
   message = "" 
  self.__indent__ -= 1
  return message

 def ondent(self, label = None, char = " ", length = __taglen__):
  return "{0}{1:{2}}".format(char*self.__indent__, label[:length-self.__indent__],length-self.__indent__)

 def __init__(self, *args, name = None, path = None, logger = logging.getLogger(__name__), **kvps):
  # When this code is executed the module importing layman.OverlayImporter 
  # is already installed within sys.modules but the importer itself is not
  # yet registered within sys.meta_path, the latter happens after __init__
  # It Ought to be possible to install the Importer in sys.Meta_Path from
  # here but this __init__ function but this might creating an undesired  
  # side effect. It does however make for a convenient one liner :
  #
  #  from layman import Overlay; OverlayImporter()
  # 
  # versus the slightly longer 
  #
  #  import sys 
  #  from overlay import OverlayImporter
  #  sys.meta_path.insert(0, OverlayImporter()) 
  #
  # Note that in both cases the class must be instantiated. Later versions
  # of importlib seem to discourage this but I do not know why.
  super().__init__(*args, **kvps)
  self.mask = "_{}_"
  self.trap = []
  self.path = {}
#   print(dir(inspect.getmodule(self)))
#   import traceback
#   from pprint import pprint
#   pprint([item for item in inspect.stack()[1:]])
#   pprint(outer('__package__'))
#   pprint(dir(inspect.stack()[1][0]))
#   print(builtin.__qualname__)
#   pprint(inspect.stack()[1][0].f_globals)
#   print(inspect.getmoduleinfo(traceback.extract_stack()[-2][0]))
#   print(inspect.getframeinfo(inspect.stack()[1][0]))
#   print(dir(inspect.stack()[1][3]))
#   print(inspect.stack()[1][3].__qualname__)
  self.name = name or inspect.getmodule(inspect.stack()[1][0]).__name__
  self.root = path or inspect.getmodule(inspect.stack()[1][0]).__path__ # Used to reference __path__ somehow
  self.log  = logger
  self.log.debug("{:{}}: {:40} {}".format(self.ondent("Instance"), self.__taglen__, str(self.__class__), [key for key in sys.modules.keys() if self.name in key]))

 # Mapping
 def pathParts(self,name) :
  """Splits the FQMN into the part for the importr and the overlay"""
  root, stem = [], []
  [root.append(part) if test else stem.append(part) for test, part in izip(self.name.split(modsep),name.split(modsep))]
  return modsep.join(root), modsep.join(stem)

 def mapToSource(self,name) :
  """Maps request to the corresponding overlay module"""
  # Consider the use of util.resolve_name(name, path)
  # Given overlay.tiers return overlay._tiers_

  return modsep.join([part if test else self.mask.format(part) for test, part in izip(self.name.split(modsep),name.split(modsep))]) 


 def mapTarget(self, name) :
  """Maps request to the overlay module"""
  # Deprecated use self.pathParts(self.mapToSource(FQMN))
  # Given overlay.tiers return tiers
  # Older Code
  return self.mask.format(name) 
  # Newer Code
  return modsep.join([part for test, part in izip(self.name.split(modsep),name.split(modsep)) if not test])
#    return modsep.join(name.split(modsep)[1:])
  
 def mapToHidden(self,name) :
  """Maps request to a corresponding hidden module"""
  # This must be run upon the output of mapToTarget
  # Given overlay.tiers or tiers return _tiers_
  
  # Older Code
  # N/A
  # Newer Code
#    for trap in self.trap :
#     parts = trap.split(modsep)
  return modsep.join([self.mask.format(part) for part in name.split(modsep)])

 def mapSource(self, name) :
  """Deprecated : Mapped the Overlay back to the module"""
  # Older Code
  mask = self.mask.split("{}")
  return name[len(mask[0]):-len(mask[-1])]
  # Newer Code
  # N/A

 def mapToSystem(self, name):
  """Maps a module to the corresponding overlay system path"""
  # This finds the first folder or file matching the module name
  # note that name must be processed beforehand using self,mapToSource
  stem = [part for test, part in izip(self.name.split(modsep),name.split(modsep)) if not test]
  test, item = tee(os.path.join(path, *stem) for path in self.root)
  path = None
  while next(test, None) : 
   path = next(item, None)
   if not os.path.isdir(path) :              # [ref:2]
    path += '.py'     
  return path

 def mapToFile(self, name):
  """ Similar to mapToSystem but for packages it tries to map to __init__.py files"""
  # Note one used to pre-map the path FQMN using mapToSource, 
  # this is done internally now
#   self.log.debug("MapToFile : {}".format(self.root))
  stem = [part for test, part in izip(self.name.split(modsep),self.mapToSource(name).split(modsep)) if not test]
  test, item = tee(os.path.join(path, *stem) for path in self.path[name])
  path = None
  while next(test, None) : 
   path = next(item, None)
#     self.log.debug(path)
   if os.path.isdir(path) :                  # [ref:3]
    path = os.path.join(path, '__init__.py') 
   else :                                    
    path += '.py'     
  return path

 def mapToRoot(self, name):
  """ Similar to mapToFile but from the Importers' Root Path"""
  # Note one used to pre-map the path FQMN using mapToSource, 
  # this is done internally now
  # This is somewhat experimental
  stem = [part for test, part in izip(self.name.split(modsep),self.mapToSource(name).split(modsep)) if not test]
  self.log.debug("{}: {} {} {} ".format(self.ondent("MapToRoot"), stem, self.root, self.path[name]))
  test, item = tee(os.path.join(path, *stem) for path in self.root) # self.path[name]
  path = None
  while next(test, None) : 
   path = next(item, None)
#     self.log.debug(path)
   if os.path.isdir(path) :                  # [ref:3]
    path = os.path.join(path, '__init__.py')
   else :                                    
    path += '.py'     
  return path

 def rename(self, name) :
  # - Deprecated
  # Currently this assumes the module is one level deep within
  # the package, that is the following structure is expected
  #
  # package\    The folder containing the __init__.py you are reading
  #  _module_   The module you are patching renamed with underscores
  #
  return modsep.join([item if enum!=1 else "_{}_".format(item) for enum, item in enumerate(name.split(modsep))])

 def overlays(self) :
  # - Deprecated
  # This is simply the list of modules that are patched under 
  # this overlay.
  # pkg.util.walkpackages is apparently useful here
  modules = [os.path.splitext(item)[0] for item in os.listdir(self.root[0]) if os.path.splitext(item)[0] not in ["__init__","__pycache__"]]
  if self.trap :
   return [self.mapSource(os.path.splitext(item)[0]) for item in modules]
  else :
   return modules

#   def find_spec(self, name, path, target = None): 
#    # One should use the module returned by find_module along
#    # with the function utils.spec_from_loader() to create a 
#    # spec for the more modern API's. 
#    #
#    # FQMN/name - name of the modules
#    # path      - path entries for the module, that is the parent packages.__path__ attribute. 
#    # target    - previous module if the current one is being reloaded, none otherwise.
#    self.log.debug("{}: {} {}".format(self.ondent("Find Spec"), name, path, target))
#  #   spec = util.find_spec(name)
#  #   self.log(spec)
#    self.loader=self
#    return self.find_module(name, path) # causes infinite recursion
#  #   return None

#  def loader(self) : 
#   return self
#   return self.load_module

 def find_module(self, name, path=None):
  # Deprecated use :
  #
  # Python > 3.3 use IMPORTLIB.UTIL.FIND_SPEC
  # Python = 3.3 use IMPORTLIB.FIND_LOADER  
  #
  # path - List of File System Path
  # name - The FQMN
  #
  bits = name.split(modsep)
  self.log.debug("{}> {:<40} {:<80}".format(self.indent("F:" + self.name),name, str(path)))
  # Overlay Layer
  if name.startswith(self.name) : # len(bits) > 1 and self.mapToHidden(bits[1]) in self.overlays(): # Note :  the clamp on bit length is to ensure the importer rolls back to root to import patched modules.
   self.path[name] = path
   self.log.debug("{0:12}: {1:<40} {2:<80}".format(self.undent("Finder"), self.mapToSource(name),__file__))
   return self
  # Standard Layer
  if bits[-1:] in self.trap :
   for meta in sys.meta_path :
    if meta is not self :
     self.temp = meta.find_module(name, path)
     if self.temp :
      self.log.debug("{}:  {1:<40}".format(self.ondent("Trapper"), name))
      return self
  self.undent()    
  return None

 def load_module(self, name):
  # Deprecated replace with the classes in IMPORTLIB.MACHINERY
  # 
  # If IMP.LOAD_MODULE was used with IMP.FIND_MODULE previously 
  # then IMPORTLIB.IMPORT_MODULE is a better substitute. If not
  # then use the loader that pairs with the prior finder. That
  # is one of :
  #
  # IMPORTLIB.UTIL.FIND_SPEC  <-> 
  # IMPORTLIB.FIND_LOADER     <->
  #   
  self.log.debug("{}: {:<40}".format(self.indent("L:" + self.name),name))
  parent, _, module = name.partition(modsep) # Was rpartition
  if name in self.trap : # This might break
   # Handle Source Import
   self.trap.pop(name)
   self.log.debug(self.ondent("Pass Trapped"))
   temp = self.temp.load_module()
   sys.modules[self.mapTarget(name)] = temp
   self.log.debug("{}< {}".format(self.undent("Imported"),self.mapTarget(name)))
#   self.dent -= 1
   return temp
  else :
   # Handle Overlay Import
#    if module not in self.overlays(): # Not Importable
#     raise ImportError("%s can only be used to import pytz!",self.__class__.__name__) # Inclde module name and possibly modules
   if module in sys.modules:           # Already Imported
    return sys.modules[module]         # Modules' absolute path
   # Import the module
   self.trap.append(module)
   # Python 3.2 API
   #self.log.debug("{}: {:40} {:40}".format(self.ondent("Loader"),self.name, name, module)) # Needs to be more useful
   #file, path, desc = imp.find_module(self.mapTarget(module), self.path)
   #try:
   # temp = imp.load_module(name, file, path, desc)
   #finally:
   # if file:
   #  file.close()
   # Python 3.3 and 3.4 API - It's a bit messy right now
   file = self.mapToRoot(name)
   _name_ = self.mapToSource(name)
   root,stem = self.pathParts(self.mapToSource(name))
   self.log.debug("{}: {:18} -> {:18} {:80}".format(self.ondent("FileLoader"),root, stem, file))
   temp = machinery.SourceFileLoader(name, file).load_module() # be weary here, re-assigning names is a bit finnicky and has a rollover impact.
   sys.modules[name] = temp # Using sys.modules[module] = temp fails
   self.log.debug("{}< {}".format(self.undent("Imported"),temp))
   return temp

if __name__ == "__main__" :
 # This section is primarily intended for developers 
 # Setup Logging
 import logging
 logging.basicConfig(format = '%(message)s')
 logger = logging.getLogger("__34__")
 logger.setLevel(logging.DEBUG)
 
 # Call Test Suites
 import unittest
 tests = {
  "all"      : 'test*.py',
  "overlay"  : '*Overlay.py',
  "uppercase": '*UpperCase.py',
  "tiers"    : '*Tiers.py',
 }
#  test = 'all'
#  suite = unittest.TestLoader().discover('..',tests[test])
#  unittest.TextTestRunner(verbosity=1).run(suite)

 __root__ = os.path.join(os.path.dirname(os.path.abspath(__file__)),'..\\help')

 sys.path.append(__root__)

 # Implicit Root Import
#  from overlay import * # Test with/out __all__ defined
 # Explicit Root Import
 from uppercase import tiers
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
#  module_a.Alpha()