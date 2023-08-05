"""
===================
Python 3.6 : ApeMan
===================

"""
# Python Compatability
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
# Flags
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
# Local Libraries
try :
 from .descriptors import PathName
 from .utilities   import Indentation
except (ModuleNotFoundError, ImportError) : # SystemError
 from descriptors  import PathName
 from utilities    import Indentation
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
 
 .. note :: This is derived from the Python 3.4 implementation.
 """

 root = PathName()
 lom = []
 # _import_ = builtins.__import__
 mask = "_{}_"

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
  # Logging and Debugging
  self.debug = debug
  if self.debug : self.log  = logging.getLogger(__name__)
  if self.debug : self.log.debug("Initialized : Import")
#   if self.debug : self.log.debug("{:{}}: {:40} {}".format(self.ondent("Instance"), self.__taglen__, str(self.__class__), [key for key in sys.modules.keys() if self.name in key]))
  # Attributes
  self.name = name or inspect.getmodule(inspect.stack()[1][0]).__name__
  self.root = root or os.path.dirname(inspect.getmodule(inspect.stack()[1][0]).__file__)
  self.mods = self.modules()
#   print(self.mods)
  # Builtins
  self._import_, builtins.__import__ = _import_, self # weakref.ref(self, self.__del__)

 def __call__(self, name, *args, **kvps) : # (self, *args, *kvps):  
  """Substitutes builtins.__import__ when one invokes an import statement

  Arguments:
   self: 
    The ApeMan instance
   name:
    The modules to be imported
   locals:
    The local scope invoking the import statement .e.g. module/function/class scope
   globals:
    The global scope invoking the import statement e.g. the module or the package scope (The __init__ file for packages)
   level:
    The relative level of the import.
  """
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
   if self.debug : self.log.debug("Redirecting : {}".format(self.name + modsep + self.mapToTarget(name)))
   return import_module(self.name + modsep + self.mapToTarget(name)) # This is a little black magic as we ignore the args
  if self.debug : self.log.debug("Importing   : {}".format(name))
  return self._import_(name, *args, **kvps)

 def mapToTarget(self, name) :
  """Maps request to the overlay module"""
  # Converts tiers.package.module to _tiers_._package_._module_
  return modsep.join([self.mask.format(part) for part in name.split(modsep)])

 def modules(self) : 
  """Lists the overlays implemented within a directory """
#  {'_docopt_' : WindowsPath('e:/python/apeman-overlays/overlays/_docopt_.py'),
#   '_pathlib_': WindowsPath('e:/python/apeman-overlays/overlays/_pathlib_.py')}  
  # This differs from overlays in that it recurses through the 
  # folder structure to find python modules
  ext = '.py'
  mod = lambda parts, ext : [part[:-len(ext)] if enum + 1 == len(parts) else part for enum, part in enumerate(parts)]
  lst = [(mod(file.relative_to(self.root).parts, ext), file) for file in self.root.rglob('*'+ext)]
  return {modsep.join(item[0][:-1]) if item[0][-1] == "__init__" else modsep.join(item[0]) : item[1] for item in lst}

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
 # Logging
 logging.basicConfig(level=logging.DEBUG) # format = '%(message)s')
 # Testing
 import unittest
 # System
#  from pathlib import Path
 # Python Path(s)
#  mockup = str(Path(os.path.dirname(os.path.abspath(__file__))).joinpath('../mockups').resolve())
#  sys.path.append(mockup)
 # Call Test Suites
 tests = {
  "all"        : 'test*.py',
  "overlay"    : '*Overlay.py',
  "assumptions": '*Assumptions.py',
  "machinery"  : '*Machinery.py',
  "scaffold"   : '*Scaffoled.py',
  "structure"  : '*Structure.py'}
 # Single tes 
#  test = 'structure'
#  suite = unittest.TestLoader().discover('..',tests[test])
#  unittest.TextTestRunner(verbosity=1).run(suite)
 # Multiple tests
 test   = ['structure']
 suite  = lambda test : unittest.TestLoader().discover('..',tests[test])
 suites = unittest.TestSuite([suite(tst) for tst in test])
 unittest.TextTestRunner(verbosity=1).run(suites)

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
