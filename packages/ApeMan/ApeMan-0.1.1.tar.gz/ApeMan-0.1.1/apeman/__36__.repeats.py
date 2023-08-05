"""
===================
Python 3.6 : ApeMan
===================

"""
# Python Compatability
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
# Constants 
DEBUG = True
# Weak references
import weakref
# System
import os
import sys
import builtins
# Types
import types
# Debugging
if DEBUG : from pdb import set_trace as db
# Inspection
import inspect
# Iteration
# from itertools import zip_longest as izip, tee # Deprecated
# Imports
from importlib import util, abc ,machinery, _bootstrap as bootstrap, import_module
import imp
from glob import glob
# Local Libraries
try :
 from .descriptors import PathName    # Remove this dependency in favour of glob
 from .utilities   import Indentation
except (ModuleNotFoundError, ImportError) : # SystemError
 from apeman.descriptors  import PathName # Remove this dependency in favour of glob
 from apeman.utilities    import Indentation
# Logging
if DEBUG : import logging
if DEBUG : log = logging.getLogger(__name__)

# Constants
modsep      = '.'
version     = (0,0,0)

class Import(Indentation):
 """
 This class replaces the `builtins.import` function with itself.
 Bypassing the ModuleSpec and Finder/Loader or Importer mechanisms.
 
 .. note :: 
 
    This is derived from the Python 3.4 implementation.
    
 .. note :: 
 
    This class is setup as a singleton and replaces builtins.__import__ with an instance of itself
 """
 
 _modules_ = []
 modules   = []

 @property
 def sources(self):
  return {modsep.join(mod) : (name, root, src) for name, root, modules in self._modules_ for mod, src in modules}

 @property
 def targets(self):
  return {modsep.join(mod) : src for name, root, modules in self.overlays for mod, src in modules}

#  root = PathName()
#  lom = []

 # The following converts ApeMan into a singleton, this is undesirable in most cases.
#  _self_ = None
#  def __new__(cls, *args, **kvps) :
#   if not isinstance(cls._self_, cls) :
#    cls._self_ = super().__new__(cls) # *args, **kvps) # This is about to cause trouble in the future
#   return cls._self_

 def __init__(self, *args, name = None, path = None, root = None, _import_ = __import__, debug = DEBUG, **kvps):
  """
  root :
   The folder from which ApeMan is invoked, this defaults to the folder containig the init file invoking ApeMan
  name :
   The package from which ApeMan is invoked, this defaults to the package invoking ApeMan, that is it maps to the folder containig the init file.
  path :
   Deprecated, this is no longer in use.
  debug :
   Deprecated, a flag to enable debugging, this will be done by configuration file in the future.
  """
  super().__init__(*args, **kvps)
  # Properties
  self.mask = "_{}_"
  # Packages
  name = name or inspect.getmodule(inspect.stack()[1][0]).__name__
  root = root or os.path.dirname(inspect.getmodule(inspect.stack()[1][0]).__file__)
  mods = self.overlays(name, root)
  if mods : 
   logging.debug(mods)
   self._modules_.append(mods) 
#   print(self.sources)
  # Logging and Debugging
  self.debug = debug
  if self.debug : self.log  = logging.getLogger(__name__)
  if self.debug : self.log.debug("Initialized : Import")
#   if self.debug : self.log.debug("{:{}}: {:40} {}".format(self.ondent("Instance"), self.__taglen__, str(self.__class__), [key for key in sys.modules.keys() if self.name in key]))
  # Import Functionality
  # Ideally the code should call self._substitute_()
  self._import_ = _import_
  builtins.__import__ = weakref.ref(self, self.__del__) # Originally weakref.proxy : https://eli.thegreenplace.net/2009/06/12/safely-using-destructors-in-python/

 # Secondary implementation
 def __call__(self, name, globals=None, locals=None, fromlist=(), level=0, **kvps) : # (self, *args, *kvps):  
  # name    - The package to be imported e.g. A.B
  # globals - The global variables for the module making the import
  # locals  - The local variables for the module making the import
  # from    - Indicates if root module, A, or submodule, B, must be imported for `import A` or `from A import B` respectively
  # level   - Relative level above module that imports must search for modules e.g. ..C -> level = 2
  """The ApeMan implementation of/subsituting :meth:`builtins.__import__`
  
  This traps the call to import MODULE and redirects to import _MODULE_.
  _MODULE_ of course imports the original MODULE and the trap is redirected.
  """
#   print("Import : {}".format(name))
#   print(globals)
#   print(self.sources)
#   print(self.mapToTarget(name))
  _module_ = next(((key, *val) for key, val in self.sources.items() if self.mapToTarget(name) == key), None)
#   module   = next(((key, *val) for key, val in self.targets.items() if self.mapToTarget(name) == key), None)
  if _module_ and not globals["__name__"] == modsep.join([_module_[1], _module_[0]]): # Include : hasattr(globals, "__name__")
   _name_, overlay, root, path = _module_
   if self.debug : self.log.debug("Substituting: {} -> {}".format(name, _name_))
#    if self.debug : self.log.debug("Gloabls     : {}".format(globals["__name__"]))
#    return self._import_(modsep.join([overlay, _name_]), globals=globals, locals=locals, fromlist=fromlist, level=level, **kvps)
   return import_module(modsep.join([overlay, self.mapToTarget(name)])) # This is a little black magic as we ignore the args
  if self.debug : self.log.debug("Importing   : {}".format(name))
  return self._import_(name, globals=globals, locals=locals, fromlist=fromlist, level=level, **kvps)

   # Original Implementation
#  def __call__(self, name, *args, **kvps) : # (self, *args, *kvps):  
#   # name    - The package to be imported e.g. A.B
#   # globals - The global variables for the module making the import
#   # locals  - The local variables for the module making the import
#   # from    - Indicates if root module, A, or submodule, B, must be imported for `import A` or `from A import B` respectively
#   # level   - Relative level above module that imports must search for modules e.g. ..C -> level = 2
#   """The ApeMan implementation of/subsituting :meth:`builtins.__import__`
#   
#   This traps the call to import MODULE and redirects to import _MODULE_.
#   _MODULE_ of course imports the original MODULE and the trap is redirected.
#   """
#   # This works as follows :
#   #  if MODULE in _MODULES_ :
#   #   if MODULE in ListOfModules :
#   #    return _MODULE_ as MODULE and register it
#   #   else :
#   #    return module
#   #  else :
#   #   return MODULE
# #   self.log.debug([{arg.get('__name__',None) or ".".join([arg["__module__"],arg["__qualname__"]]):arg.keys()} if isinstance(arg, dict) else arg for arg in args]) # Globals has __name__ and Locals has __qualname__ and __module__ 
#   if self.mapToTarget(name) in self.mods.keys() :
#    self.log.debug("Mapping     : {} -> {}".format(name, self.mapToTarget(name)))
#    self.log.debug([{arg['__name__']:[]} if isinstance(arg, dict) else arg for arg in args])
#    if self.debug : self.log.debug("Overloading : {}".format(name))
#    if name in self.lom :
#     if self.debug : self.log.debug("Importing   : " + name)
#     return self._import_(name, *args, *kvps)
# #    self.log.debug("remap : " + name + " -> "+ self.name + "." +self.mapToTarget(name))
# #    self.log.debug(name)
# #    self.log.debug(self.name + modsep + self.mapToTarget(name))
# #    self.log.debug("Wrapped Import")
#    self.lom.append(name)
#    if self.debug : self.log.debug("Redirecting : {}".format(self.name + modsep + self.mapToTarget(name)))
#    return import_module(self.name + modsep + self.mapToTarget(name)) # This is a little black magic as we ignore the args
#   if self.debug : self.log.debug("Importing   : {}".format(name))
#   return self._import_(name, *args, **kvps)

 def mapToTarget(self, name):
  """Maps request to the overlay module
  
  Given the name for a modules, `MODULE`, map this to an overlay, `_MODULE_`.
  Longer paths are handled somewhat simply at the moment e.g.  `PACKAGE.MODULE` is simply ampped to `_PACKAGE_._MODULE_` versus say `PACKAGE._MODULE_`.
  """
  # Converts tiers.package.module to _tiers_._package_._module_
  return modsep.join([self.mask.format(part) for part in name.split(modsep)])

 def overlays(self, name, root) : 
  """Lists the overlays implemented within a directory """
  # This differs from overlays in that it recurses through the 
  # folder structure to find python modules
  #
  # Note : It is more useful for this fucntion to return the overlay tuple then it is for it to append it directly to self._modules_
  ext = '.py'
  # This version quashed the __init__ file somehow
#   mod = lambda parts, ext : [part[:-len(ext)] if enum + 1 == len(parts) else part for enum, part in enumerate(parts)] # This should really use os.path.splitext
#   lst = [(mod(os.path.relpath(file,root).split(os.path.sep), ext), file) for file in glob(os.path.join(root, '*' + ext), recursive = True)]
  mod = lambda root, path : tuple((os.path.splitext(os.path.relpath(path, root))[0]).split(os.path.sep))
  lst = [(mod(root, file), file) for file in glob(os.path.join(root, '*' + ext), recursive = True)]
#   print([(os.path.relpath(file,root)) for file in glob(os.path.join(root, '*' + ext), recursive = True)])
#   new = {modsep.join(item[0][:-1]) if item[0][-1] == "__init__" else modsep.join(item[0]) : item[1] for item in lst}
#   print(self._modules_)
  self._modules_.append((name, root, lst)) # Root is a bit redundant
#   print((name, root, lst))
#   print(self._modules_)
  
  # The code here stores the modules in a bit of a convoluted manner
#   self.mods = new
#   self.modules[(name,root)] 
#   self.modules.update((name,root,modules,{})) # Be weary not to

#  def __repr__(self) :
#   return str(self.__class__, self.name, self.path)
#  def __str__(self) :
#   return str(self.__class__, self.name, self.path)

 def __del__(self):
  """
  The recommended method for removing an instance of ApeMan is to call __del__ on a reference ones retains for this purpose.
  :: 
    apeman = ApeMan()
    apeman.__del__()

  If one has not retained a reference for this purpose then the following call may be used instead.
  :: 
    ApeMan()
    builtins.__import__.__del__()
  """
#   print("__del__")
#   self._substitute_()
  builtins.__import__ = self._import_
  
 def _substitute_(self, apply = None):
  """DEPRECATED : Substitute the current builtins.__import__ for self and vice versa.
  
  It is assumed that this is called twice, once by __init__ and once by __del__.
  It does not track staate properly and calling the function outside of these contexts should not really be done.
  There might be a better implementation, such as splitting it into two functions to either apply or revert the substitution.
  """
  # [1] describes how a weak reference might be used to prevent a concrete reference to the class.
  # This allows for the deletion of the class from a concrete reference.
  # This must be considered if we make ApeMan into a singleton.
  # [1]https://stackoverflow.com/a/3014477
  if apply is None : 
   if builtins.__import__ == self : # Previously, When Import was a Singleton : builtins.__import__ == _import_
    builtins.__import__ = self._import_
   else : 
    print("revert")
    builtins.__import__ = weakref.ref(self) # This was weakref.proxy : https://eli.thegreenplace.net/2009/06/12/safely-using-destructors-in-python/
 #    builtins.__import__ = self 

class OverlayImporter(abc.MetaPathFinder, Indentation): # , abc.SourceLoader
 """
 This class combines a Finder and a Loader into an Importer. 

 .. inheritance-diagram:: apeman.__34__
    :parts:      2

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

 root = PathName()
 lom = []

 def __init__(self, *args, name = None, path = None, root = None, _import_ = __import__, **kvps):
  """
  name :
   The name of the module that ApeMan is invoked from. 
   That is the __init__ file in the overlays' folder.
  root :
   The folder where ApeMan is invoked from
   That is the __init__ file in the overlays' folder.
  path : 
   DEPRECATED, not sure of the original purpose, presumably the older code may have this documented otherwise one might have intended it be used to project that the root of the overlay was relative to the root of the invoking space.
  _import_ :  
   This should not be set unless you are really trying to break things, it defaults to the builtin.__import__
  """
  if DEBUG : log.debug("OverlayImporter Initialized")
  super().__init__(*args, **kvps)
  # Importer Functionality
  self.mask = "_{}_"
  self.trap = {}
  self.wrap = {}
  self.name = name or inspect.getmodule(inspect.stack()[1][0]).__name__
  self.root = root or os.path.dirname(inspect.getmodule(inspect.stack()[1][0]).__file__)
  self.mods = self.modules()
  if DEBUG : self.log  = logging.getLogger(__name__)
  if DEBUG : self.log.debug("{:{}}: {:40} {}".format(self.ondent("Instance"), self.__taglen__, str(self.__class__), [key for key in sys.modules.keys() if self.name in key]))
  # Import Functionality
#   builtins.__import__ = self
#   self._import_ = _import_

 def __call__(self, name, *args) : # (self, *args, *kvps):  
  # Hooks the import statement
#   self.log.debug("importing : {}".format(name))
#   self.log.debug([{arg['__name__']:arg.keys()} if isinstance(arg, dict) else arg for arg in args])
#   if self.mapToTarget(name) in self.mods.keys() :
#    self.log.debug("Overloaded")
#    if name in self.lom :
#     self.log.debug("unmap : " + name)
#     return self._import_(name, *args)
#    self.log.debug("remap : " + name + " -> "+ self.name + "." +self.mapToTarget(name))
#    self.log.debug(name)
#    self.log.debug(self.name + modsep + self.mapToTarget(name))
#    self.log.debug("Wrapped Import")
#    self.lom.append(name)
#    return import_module(self.name + modsep + self.mapToTarget(name)) # This is a little black magic as we ignore the args
  if DEBUG : log.debug("import called : {}".format(name))
  return self._import_(name, *args)

 def mapToTarget(self, name) :
  """Maps request to the overlay module"""
  # Converts tiers.package.module to _tiers_._package_._module_
  return modsep.join([self.mask.format(part) for part in name.split(modsep)])

 def modules(self) : 
  """ Lists the overlays implemented within a directory """
  # This differs from overlays in that it recurses through the 
  # folder structure to find python modules
  ext = '.py'
  mod = lambda parts, ext : [part[:-len(ext)] if enum + 1 == len(parts) else part for enum, part in enumerate(parts)]
  lst = [(mod(file.relative_to(self.root).parts, ext), file) for file in self.root.rglob('*'+ext)]
  return {modsep.join(item[0][:-1]) if item[0][-1] == "__init__" else modsep.join(item[0]) : item[1] for item in lst}

#  def get_data() :
#   pass
  
#  def get_filename() :
#   pass 
  
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

#  def find_module(self, name, path=None):
# #   self.log.debug("Find_module")
#   self.log.debug("{}> {:<40} {:<80}".format(self.indent("F:" + self.name),name, str(path)))
# #   self.log.debug([sys.modules[key] for key in sys.modules.keys() if name in key])
#   if self.mapToTarget(name) in self.mods :                    # User imports _PACKAGE_
# #    self.log.debug(self.undent("F:Trap"))
#    self.trap[name] = self.mods.pop(self.mapToTarget(name))
#    return self
#   if self.trap.pop(name) :                                    # overlay imports PACKAGE
# #    self.log.debug(self.undent("F:Wrap"))
#    for meta in [meta for meta in sys.meta_path if meta is not self]:
#     self.wrap[name] = self.wrap.get(name) or meta.find_module(name, path)
#    return self
# #   if name in self.wrap :                                      # overlay imports PACKAGE
# #    return self
#   return None
 
#  def load_module(self, name):
# #   self.log.debug("{}: {:<40}".format(self.indent("L:" + self.name),name))
#   load = sys.modules.get(name)
#   if name in self.trap :
#    # One should strictly use SourceFileLoader here instead.
# #    self.log.debug(self.ondent("L:Trap"))
#    file = self.trap.get(name)
#    load = types.ModuleType(self.mapToTarget(name))
#    with file.open('r') as data : code = data.read()
# #    self.log.debug([key for key in sys.modules.keys() if name in key])
#    load.__file__ = str(file)
#    code = compile(code, str(file), 'exec')
#    sys.modules[name] = load # must occur before exec
#    exec(code, load.__dict__)
# #    self.log.debug([key for key in sys.modules.keys() if name in key])
# #    self.log.debug(load.__version__)
#   if name in self.wrap :
#    # Note : importing PACKAGE as _PACKAGE_ fails. 
#    # This is due to the to the `builtin` importers preventing
#    # name changes. To be explicit they can't find a funny 
#    # named module and one can't cross assign the module. One
#    # can reassign it however
# #    self.log.debug(self.ondent("L:Wrap"))
#    spec = self.wrap.pop(name)
#    load = spec.load_module()
# #   self.log.debug([sys.modules[key] for key in sys.modules.keys() if name in key])
# #   self.log.debug(self.undent("L:Done"))
#   return load
  
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
 # External call
#  from pathlib import Path
#  path = str(Path(os.path.dirname(os.path.abspath(__file__))).joinpath('../mockups').resolve())
#  sys.path.append(path)
#  from subprocess import Popen, PIPE # check_output as cmd, CalledProcessError
# #  code = \
# # """
# # import logging; logging.basicConfig(level=logging.INFO); logging.info(__name__)
# # import uppercaseWithInit
# # """
# #  code = \
# # """
# # import logging; logging.basicConfig(level=logging.INFO); logging.info(__name__)
# # from withInit_a.module_a import ClassA
# # """
#  code = \
# """
# import overlay
# # import logging as log; log.basicConfig(level=log.DEBUG); log.info(__name__)
# from module import ClassA
# print(ClassA())
# """
#  command = Popen([sys.executable,"-c",code], stdout=PIPE, stderr=PIPE, cwd = path)
#  output, error = command.communicate()
#  print("Process Messages")
#  print(output.decode())
#  print("Error Messages")
#  print(error.decode())

 # Logging
 logging.basicConfig(level=logging.DEBUG) # format = '%(message)s')
 # System
 from pathlib import Path
 # Python Path(s)
 __root__ = str(Path(os.path.dirname(os.path.abspath(__file__))).joinpath('../mockups').resolve())
 sys.path.append(__root__)

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

 # Atomic Imports
#  import uppercaseWithInit
#  logger.debug([sys.modules[key] for key in sys.modules.keys() if 'tiers' in key])
# #  logger.debug("Primary")
# #  import tiers
# #  logger.debug([sys.modules[key] for key in sys.modules.keys() if 'tiers' in key])
# #  logger.debug(tiers.__file__)
# #  logger.debug(tiers.__version__)
#  logger.debug("Secondary")
#  from tiers import package_a
#  logger.debug([key for key in sys.modules.keys() if 'tiers' in key])
#  logger.debug([sys.modules[key] for key in sys.modules.keys() if 'os' in key])
#  logger.debug(package_a.__version__)
#  from tiers import module_a
#  logger.debug([key for key in sys.modules.keys() if 'tiers' in key])
#  logger.debug([sys.modules[key] for key in sys.modules.keys() if 'os' in key])
#  logger.debug(module_a.ClassA())
#  logger.debug("\nTertiary")
#  from tiers.package_a import module_b
#  logger.debug([key for key in sys.modules.keys() if 'tiers' in key])
#  logger.debug([sys.modules[key] for key in sys.modules.keys() if 'os' in key])
# #  logger.debug(module_b.ClassB())

#  db()
 
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

# else :
#  import builtins
#  def _import_(*args, importer = __import__) :
#   # Hooks the import statement
#   logger.debug("import : {}".format(args[0]))
#   temp = importer(*args)  
# #   logger.debug(dir(temp))
#   logger.debug([temp.__name__, temp.__file__, temp.__package__, temp.__loader__])
#   return temp
#  builtins.__import__ = _import_ 

 # Pass
 pass
