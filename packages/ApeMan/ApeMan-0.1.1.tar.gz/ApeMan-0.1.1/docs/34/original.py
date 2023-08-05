# This is a documentation copy of the original code in :
#
#   apeman\__34__.original.py
"""
This was the original version that I managed to get working
"""
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
 
# if __debug__ :
 dent = 0
 def indent(self, label = None, char = " ", length = 12):
  message = "{0}{1:{2}}".format(char*self.dent, label[:length-self.dent],length-self.dent)
  self.dent += 1
  return message

 def undent(self, label = None, char = " ", length = 12):
  message = "{0}{1:{2}}".format(char*self.dent, label[:length-self.dent],length-self.dent)
  self.dent -= 1
  return message

 def ondent(self, label = None, char = " ", length = 12):
  return "{0}{1:{2}}".format(char*self.dent, label[:length-self.dent],length-self.dent)

 def __init__(self, *args, name = None, path = None, logger = logging.getLogger(__name__), **kvps):
  super().__init__(*args, **kvps)
  self.mask = "_{}_"
  self.trap = None
  self.name = name or inspect.getmodule(inspect.stack()[1][0]).__name__
  self.path = path or inspect.getmodule(inspect.stack()[1][0]).__path__ # Used to reference __path__ somehow
  self.log  = logger
  self.log.debug("{:12}: {}".format(self.ondent("Instance"), self.__class__))

 def mapTarget(self, name) :
  """Maps request to the overlay module"""
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


 def rename(self, name) :
  # Currently this assumes the module is one level deep within
  # the package, that is the following structure is expected
  #
  # package\    The folder containing the __init__.py you are reading
  #  _module_   The module you are patching renamed with underscores
  #
  return modsep.join([item if enum!=1 else "_{}_".format(item) for enum, item in enumerate(name.split(modsep))])

 def overlays(self) :
  # This is simply the list of modules that are patched under 
  # this overlay.
  # pkg.util.walkpackages is apparently useful here
  modules = [os.path.splitext(item)[0] for item in os.listdir(self.path[0]) if os.path.splitext(item)[0] not in ["__init__","__pycache__"]]
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
#    self.log.debug("{:12}: {} {}".format(self.ondent("Find Spec"), name, path, target))
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
  bits = name.split(modsep)
  self.log.debug("{0:12}> {1:<40} {2:<80}".format(self.indent("Find Mods"),name, str(path)))
  if len(bits) > 1 and self.mapTarget(bits[-1]) in self.overlays(): # Note :  the clamp on bit length is to ensure the importer rolls back to root to import patched modules.
   self.path = path
   self.log.debug(" "*self.dent + "Discovered : {0:<40} {1:<80}".format(name,__file__))
   return self
  if bits[-1] == self.trap :
   for meta in sys.meta_path :
    if meta is not self :
     self.temp = meta.find_module(name, path)
     if self.temp :
      self.log.debug(" "*self.dent + "Discovered : {}".format(name))
      return self
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
#  self.dent += 1
  self.log.debug(" "*self.dent + "Importing  > {}".format(name))
  parent, _, module = name.rpartition(modsep)
  if self.trap :
   self.trap = None
   self.log.debug(" "*self.dent + "Pass Trapped")
   temp = self.temp.load_module()
   sys.modules[self.mapTarget(name)] = temp
   self.log.debug(" "*self.dent + "Imported   < {}".format(self.mapTarget(name)))
#   self.dent -= 1
   return temp
  else :
   self.log.debug(" "*self.dent + "Pass Through {}".format(module))
#    if module not in self.overlays(): # Not Importable
#     raise ImportError("%s can only be used to import pytz!",self.__class__.__name__) # Inclde module name and possibly modules
   if name in sys.modules:           # Already Imported
    return sys.modules[name]         # Modules' absolute path
   self.trap = module
   file, path, desc = imp.find_module(self.mapTarget(module), self.path) # NB !!! This was psuedo 
   try:
    temp = imp.load_module(name, file, path, desc)
   finally:
    if file:
     file.close()
   sys.modules[module] = temp
   self.log.debug("{:10} < {}".format(self.undent("Imported"),module))
   return temp
 
if __name__ == "__main__" :
#  print("Main")
 import logging
 logging.basicConfig(format = '%(message)s')
 logger = logging.getLogger("__34__")
 logger.setLevel(logging.DEBUG)
 
 __root__ = os.path.join(os.path.dirname(os.path.abspath(__file__)),'..\\tests')
 sys.path.append(__root__)

 # General Import
#  from overlay import *
 # Targeted Import
#  from overlay import tiers
 # Nested Import
#  from overlay.tiers import first
 # Staggered Import
 from uppercase import tiers 
 logger.debug("Modules     : {}\n".format([key for key in sys.modules.keys() if key.startswith('overlay') or key.startswith('tiers')]))
 from tiers   import module_a
 logger.debug("Modules     : {}\n".format([key for key in sys.modules.keys() if 'overlay' in key or 'tiers' in key]))
#  logger.debug("\n".join(["{:24} : {}".format(key, sys.modules[key]) for key in sys.modules.keys() if key.startswith('overlay') or key.startswith('tiers')]))
