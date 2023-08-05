#! Python27
"""
Since ModuleSpec's in Python 3.4 onwards prevent the cross assignment of modules under :attr:`sys.modules` it forces one to actively redirect imports.
As a result the Python 2.7 implementation of ApeMan must conform to its later implementations.

"""
# Python 2.7 Compatability
# from __future__ import absolute_import
# from __future__ import division
# from __future__ import print_function
# from __future__ import unicode_literals
# from builtins import super
# from builtins import range
# from builtins import str
# from future import standard_library
# standard_library.install_aliases()
# 
# from builtins import *
# import builtins
import __builtin__
# System
import os
import sys
# Imports
import imp
# Types
import types
# Inspection
import inspect
# Paths
from pathlib import Path
# Iteration
from itertools import izip_longest as izip, tee
# Descriptors
from descriptors import FileName, PathName, RootName
# Utilities
from utils import Indentation
# Logging
import logging
# Debugging
# from pdb import set_trace as db

# Constants
modsep      = '.'
version     = (0,0,0)

class Import(Indentation):
 """Substitutes :attr:`__builtins__.__import__` with itself to load patched versions of other modules
 
 :class:`Import` substitutes the :attr:`__builtins__.__import__` function with itself.
 This allows it to intercept later imports substituing the source module, containing the original code, with the target module, the patch for the source module.
 The target module necessarily imports the source module a second time; forcing :class:`Import` to either track the imports it's seen or inspect the origin requesting the import.
 """

 root = PathName()
 lom = []
 mask = "_{}_"

 def __init__(self, *args, **kvps): # Originally : def __init__(self, *args, name = None, path = None, root = None, _import_ = __import__, debug = DEBUG, **kvps):
  """
  root :
   The folder from which ApeMan is invoked, this defaults to the folder containig the init file invoking ApeMan
  name :
   The package from which ApeMan is invoked, this defaults to the package invoking ApeMan, that is it maps to the folder containig the init file.
  debug :
   Flag enabling debugging, hopefully this will be done by configuration file in the future.
  """
  # Python 2.7 Compatability
#   kvps['path'] if 'path' in kvps
  # Original code
  super(Import, self).__init__(*args, **kvps)
  # Logging and Debugging
  self.debug = kvps['debug'] if 'debug' in kvps else True
  if self.debug : self.log  = logging.getLogger(__name__)
  if self.debug : self.log.debug("Initialized : Import")
  # Attributes
#   self.name = kvps['scope'] if 'name' in kvps else inspect.getmodule(inspect.stack()[1][0]).__name__
  self.name = kvps['name']  if 'name' in kvps else inspect.getmodule(inspect.stack()[1][0]).__name__
  self.root = kvps['root']  if 'root' in kvps else os.path.dirname(inspect.getmodule(inspect.stack()[1][0]).__file__)
  self.mods = self.modules()
  if self.debug : self.log.debug("Modules     : {}".format(str(sorted(self.mods.keys()))))
#   if self.debug : self.log.debug("{:{}}: {:40} {}".format(self.ondent("Instance"), self.__taglen__, str(self.__class__), [key for key in sys.modules.keys() if self.name in key]))
  # Builtins
  self._import_ =  __builtin__.__import__ # kvps['_import_'] if '_import_' in kvps else 
  __builtin__.__import__ = self # weakref.ref(self, self.__del__)
#   sys.path.append(self.root)

 def __call__(self, name, *args, **kvps) : # (self, *args, *kvps):  
  """
  In Python 2.7 :meth:`__builtins__.__import__` loads a module in two stages. 
  The first, :meth:`imp.find_module`, searches ones system for the given module, returning a tuple containing the components to load the module.
  This tuple, referred to as a :class:`ModuleSpec` from Python 3.4 onwards, is passed to the second function :meth:`imp.load_module` which performs the actual loading.
  ::

    spc = imp.find_module("PACKAGE.MODULE", [str(Path.cwd()/"OVERLAY")])
    mod = imp.load_module("PACKAGE.MODULE", *spc) 
    
  The job of :meth:`Import.__call__` is to redirect the initial import for a matching patch to the patched target.
  The patch invariably triggers a second import which  :meth:`Import.__call__` should direct to the original unptched source.
  
  The call signature for __import__ is as follows 
   name 
    The module name that is to be imported
   globals 
    The globals for the calling modules scope
   locals
    The locals for the calling modules scope
   fromlist
    The list of items to be imported from the module
   level
    The relative level from the calling modules scope that the import is to be made from e.g. module -> level = 0, .module -> level = 1, ..module -> level = 2.
  """
  # Pythons `MOTW`_ describes how the path containing the module should be the one one searches for a module hence the ugly line
  # ::
  #   spc = imp.find_module(self.mapToTarget(name).split(modsep)[-1] if self.mods[self.mapToTarget(name)].stem != "__init__" else "__init__", [str(self.mods[self.mapToTarget(name)].parent)]) # [str(self.root)])
  #
  # .. _MOTW: https://pymotw.com/2/imp/#finding-modules
  # Hooks the import statement
#   self.log.debug([{arg['__name__']:arg.keys()} if isinstance(arg, dict) else arg for arg in args])
  if self.mapToTarget(name) in self.mods.keys() :
#    if self.debug : self.log.debug("Overloading : {}".format(name))
   if name in self.lom :
    if self.debug : self.log.debug("Reverting   : " + name)
    return self._import_(name, *args, **kvps)
#    self.log.debug("remap : " + name + " -> "+ self.name + "." +self.mapToTarget(name))
#    self.log.debug(name)
#    self.log.debug(self.name + modsep + self.mapToTarget(name))
#    self.log.debug("Wrapped Import")
   self.lom.append(name)
   if self.debug : self.log.debug("Diverting   : {}".format(self.name + modsep + self.mapToTarget(name)))
#    return import_module(self.name + modsep + self.mapToTarget(name)) # This is a little black magic as we ignore the args
   if self.debug : self.log.debug(self.mapToTarget(name) + " >>---> " + str(self.mods[self.mapToTarget(name)].parent))
   spc = imp.find_module(self.mapToTarget(name).split(modsep)[-1] if self.mods[self.mapToTarget(name)].stem != "__init__" else "__init__", [str(self.mods[self.mapToTarget(name)].parent)]) # [str(self.root)])
   if self.debug : self.log.debug(spc)
   mod = imp.load_module(self.mapToTarget(name), *spc)
   if self.debug : self.log.debug(mod)
   return mod
#   if self.debug : self.log.debug("Importing   : {}".format(name))
  return self._import_(name, *args, **kvps)

 def mapToTarget(self, name) :
  """Maps request to the target module, that is the patch in the overlay"""
  # Converts tiers.package.module to _tiers_._package_._module_
  return modsep.join([self.mask.format(part) for part in name.split(modsep)])

 def mapToSource(self,name) :
  """Maps request to the source module, that is the original module"""
  # Converts _tiers_._package_._module_ to tiers.package.module
#   try : 
  mask = self.mask.split("{}")
  source = lambda text : text[(text[:len(mask[0])]==mask[0])*len(mask[0]):len(text)-len(mask[-1])*(text[-len(mask[-1]):]==mask[-1])] # Originally : source = lambda name : name[len(mask[0]):-len(mask[-1])]
  return modsep.join([source(part) for part in name.split(modsep)])
#   except AttributeError as error :
#    return ""

 def modules(self) : 
  """Lists the overlays implemented within a directory """
  # This differs from overlays in that it recurses through the 
  # folder structure to find python modules
  ext = '.py'
  mod = lambda parts, ext : [part[:-len(ext)] if enum + 1 == len(parts) else part for enum, part in enumerate(parts)]
  lst = [(mod(file.relative_to(self.root).parts, ext), file) for file in self.root.rglob('*'+ext)]
  return {modsep.join(item[0][:-1]) if item[0][-1] == "__init__" else modsep.join(item[0]) : item[1] for item in lst}
#   self.log.debug(lst)
#  lst = {(self.mapToSource(modsep.join(item[0][:-1])),modsep.join(item[0][:-1])) if item[0][-1] == "__init__" else (self.mapToSource(modsep.join(item[0])),modsep.join(item[0])) : item[1] for item in lst}
#  # Originally : lst = {modsep.join(item[0][:-1]) if item[0][-1] == "__init__" else modsep.join(item[0]) : item[1] for item in lst}
#  if self.debug : self.log.debug("Overlays    : {}".format(str(lst.keys())))
#  return lst 

 def __del__(self):
  """
  The recommended method for removing an instance of ApeMan is to call __del__ on a reference ones retains for this purpose.
  :: 
    apeman = ApeMan()
    apeman.__del__()

  If one has not retained a reference for this purpose then the following call may be used instead.
  :: 
    ApeMan()
    __builtins__['__import__'].__del__()
  """
#   __builtins__['__import__'] = self._import_
  __builtin__.__import__ = self._import_

class OverlayFinder(Indentation, object) :
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

class OverlayImporter(object) : # (abc.MetaPathFinder, abc.Loader):
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
#  root = RootName() # Descriptors not supported in Python 2.7 I think
 
 def __init__(self, *args, **kvps):
  kvps['name'] = kvps.get('name', inspect.getmodule(inspect.stack()[1][0]).__name__)
  kvps['root'] = kvps.get('root', Path(os.path.dirname(inspect.getmodule(inspect.stack()[1][0]).__file__)))
  kvps['path'] = kvps.get('path', None) # I'm not sure this is relevant
  super(OverlayImporter, self).__init__() # *args, **kvps)
  self.mask = "_{}_"
  self.trap = {}
  self.name = kvps['name'] or inspect.getmodule(inspect.stack()[1][0]).__name__
  self.root = kvps['root'].parent if kvps['root'].is_file() else kvps['root'] # Python 3 : kvps['root'] or os.path.dirname(inspect.getmodule(inspect.stack()[1][0]).__file__)
  self.mods = self.modules()
  self.log  = logging.getLogger(__name__)
#   self.log.debug("{:{}}: {:40} {}".format(self.ondent("Instance"), self.__taglen__, str(self.__class__), [key for key in sys.modules.keys() if self.name in key]))
  
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

 def find_module(self, name, path=None):
#   self.log.debug("{}> {:<40} {:<80}".format(self.indent("F:" + self.name),name, str(path)))
  # Overlay Layer
  temp = self.mods.get(self.mapToTarget(name))
  if temp :
   if name in self.trap : 
    # overlay imports PACKAGE
#     self.log.debug(self.ondent("Wrap"))
    for meta in [meta for meta in sys.meta_path if meta is not self]:
     self.wrap[name] = self.wrap.get(name) or meta.find_module(name, path)
    return self
   else :
    # User imports _PACKAGE_
#     self.log.debug(self.ondent("Trap"))
    self.trap[name] = temp
    return self
  return None 
 
 def load_module(self, name):
#   self.log.debug("{}: {:<40}".format(self.indent("L:" + self.name),name))
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
#     self.log.debug([key for key in sys.modules.keys() if name in key])
    load.__file__ = str(file)
    code = compile(code, str(file), 'exec')
    exec(code, load.__dict__)
    sys.modules[name] = load
#     self.log.debug([key for key in sys.modules.keys() if name in key])
#     self.log.debug(load.__version__)
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
 # Finders
 # =======
 # This simply ensures that one can find a module, whether it is a patch or not.
#  name = "_module_"
#  path = "e:\\python\\apeman\\mockup\\explicitImport\\_explicit_"
#  spc = imp.find_module(name, [path])
#   mask = "_{}_"
#   mapToTarget = lambda name : modsep.join([mask.format(part) for part in name.split(modsep)])
#   path = Path.cwd().parents[1]/"mockup"/"overlay"
#   spc = imp.find_module(mapToTarget(name), [str(path)])
#   spc = imp.find_module("_module_", ["E:\\Python\\apeman\\mockup\\overlay"])
#  print(spc)
 

 # Demonstration
 # =============
 # This invokes ApeMan through the example.py file in the mockup directory.
 # The example loads an overlay and should import a patch, overlay/_module_.py, over the original module, module.py.
 import subprocess as su
 # Example 27 
 # ==========
 # This uses the ping pong importer over the usual one provided by ApeMan.
#  su.check_output("C:\\Python\\64bit\\2714\\python.exe example27.py",      cwd = "e:\\python\\apeman\\mockup") #  shell = True, stderr=su.STDOUT)
 # Example 27 
 # ==========
 # This uses the ping pong importer over the usual one provided by ApeMan.
 su.check_output("C:\\Python\\64bit\\2714\\python.exe explicitImport.py", cwd = "e:\\python\\apeman\\mockup") #  shell = True, stderr=su.STDOUT)
 
#  # Compatability
#  import six
#  # Logging
#  logging.basicConfig(level=logging.DEBUG) # format = '%(message)s')
#  # Testing
#  import unittest2 as unittest
#  # Test Selection
#  test   = ['explicit','implicit','versions']
#  # Test Configuration
#  tests = {
#   "all"        : 'test*.py',
#   "overlay"    : '*Overlay.py',
#   "assumptions": '*Assumptions.py',
#   "machinery"  : '*Machinery.py',
#   "explicit"   : '*Explicit.py',
#   "implicit"   : '*Implicit.py',
#   "versions"   : '*Init.py',
#   "structure"  : '*Structure.py'}
#  test = test or ['all']
#  suite  = lambda test : unittest.TestLoader().discover('../..',tests[test])
#  suites = unittest.TestSuite([suite(tst) for tst in test])
#  unittest.TextTestRunner(verbosity=1).run(suites)

#  # Setup Logging
#  import logging
#  logging.basicConfig(format = '%(message)s')
#  logger = logging.getLogger(__name__) # "__34__"
#  logger.setLevel(logging.DEBUG)
#  
#  # Call Test Suites
#  import six
#  import unittest
#  tests = {
#   "all"      : 'test*.py',
# #   "overlay"  : '*Overlay.py',
# #   "uppercase": '*UpperCase.py',
# #   "tiers"    : '*Tiers.py',
#   "explicit" : '*Explicit.py',
#   "implicit" : '*Implicit.py',
#  }
#  # Single tests
# #  test = 'explicit'
# #  suite = unittest.TestLoader().discover('..',tests[test])
# #  unittest.TextTestRunner(verbosity=1).run(suite)
#  # Multiple tests
#  test   = ['explicit', 'implicit']
#  suite  = lambda test : unittest.TestLoader().discover('../tests',tests[test])
#  suites = unittest.TestSuite([suite(t) for t in test])
#  unittest.TextTestRunner(verbosity=1).run(suite)

#  Import(root = str(Path.cwd()/".."/"mockup"))
#  import module

#  __root__ = os.path.join(os.path.dirname(os.path.abspath(__file__)),'..\\tests')
# 
#  sys.path.append(__root__)
# 
#  # Atomic Imports
#  import uppercase
# #  print([key for key in sys.modules.keys() if 'tiers' in key])
#  import tiers
#  import tiers
# #  print([key for key in sys.modules.keys() if 'tiers' in key])
#  print(tiers.__version__)
#  # Implicit Root Import
# #  from overlay import * # Test with/out __all__ defined
#  # Explicit Root Import
# #  from uppercase import tiers
#  # Explicit Nested import
# #  from overlay.tiers import module_a
#  # Explicit Nested import
# #  from overlay.tiers.module_a import Alpha
# #  print(Alpha())
#  # Explicit Staged import
# #  from overlay import tiers 
# #  logger.debug("Modules     : {}\n".format([key for key in sys.modules.keys() if key.startswith('overlay') or key.startswith('tiers')]))
# #  from tiers   import module_a
# #  logger.debug("Modules     : {}\n".format([key for key in sys.modules.keys() if 'overlay' in key or 'tiers' in key]))
# #  logger.debug("\n".join(["{} : {}".format(key, sys.modules[key]) for key in sys.modules.keys() if key.startswith('overlay') or key.startswith('tiers')]))
