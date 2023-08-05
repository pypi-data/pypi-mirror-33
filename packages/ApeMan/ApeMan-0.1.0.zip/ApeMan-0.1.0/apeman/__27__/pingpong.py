#! python27
"""
The :class:`Import` here provides the cleanest ApeMan implementation.
It allows an overlay with the following structure structure
::

   OVERLAY
    __init_.py
    _MODULE_.py
    
Where `_MODULE_.py` simply imports itself ::

   from _MODULE_ import *
   
   ...

ApeMan readily switches between the target patch and the source module.
The diversion to the patch simply tests if there is a patch with a matching name and the reversion to the module simply does the reverse.
That is one simply maps back and forth from :mod:`package.module` and to :mod:`_package_._module_`.
Allowing :class:`Import` to be stateless.
Additionally it correctly swaps the module that is loaded under the others name in :attr:`sys.modules`, providing a passive guarantee that once loaded the patch is always looked up in favour of the unpatched module.
"""
# Builtins
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

class Import(Indentation):
 """Substitutes :attr:`__builtins__.__import__` with itself to load patched versions of other modules
 
 :class:`Import` substitutes the :attr:`__builtins__.__import__` function with itself.
 This allows it to intercept later imports substituing the source module, containing the original code, with the target module, the patch for the source module.
 The target module necessarily imports the source module a second time; forcing :class:`Import` to either track the imports it's seen or inspect the origin requesting the import.
 """

 root = PathName()

 def __init__(self, *args, **kvps): # Originally : def __init__(self, *args, name = None, path = None, root = None, _import_ = __import__, debug = DEBUG, **kvps):
  """Instantiates ApeMan assigning it as a default importer in :attr:`_builtin__.__import__`
  
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
  # Properties
  self.mask = "_{}_"
  self.debug = kvps['debug'] if 'debug' in kvps else False
  if self.debug : self.log  = logging.getLogger(__name__)
  if self.debug : self.log.debug("Initialized : Import")
#   self.name = kvps['scope'] if 'name' in kvps else inspect.getmodule(inspect.stack()[1][0]).__name__
  self.name = kvps['name']  if 'name' in kvps else inspect.getmodule(inspect.stack()[1][0]).__name__
  self.root = kvps['root']  if 'root' in kvps else os.path.dirname(inspect.getmodule(inspect.stack()[1][0]).__file__)
  self.mods = self.modules()
  # Logging and Debugging
#   if self.debug : self.log.debug("Modules     : {}".format(str(self.mods.keys())))
#   if self.debug : self.log.debug("{:{}}: {:40} {}".format(self.ondent("Instance"), self.__taglen__, str(self.__class__), [key for key in sys.modules.keys() if self.name in key]))
  # Import Functionality
  self._import_ =  __builtin__.__import__ # kvps['_import_'] if '_import_' in kvps else 
  __builtin__.__import__ = self # weakref.ref(self, self.__del__)
#   sys.path.append(self.root)

 def __call__(self, name, *args, **kvps) : # (self, *args, *kvps):  
  """
  :class:`Import` needs to track whether the source, the original package, or the target, a patch in the overlay, is being loaded. 
  This may be done statelessly by comparing the module argument, that is the module being imported, to the :attr:`__package__` attribute, the origin, of the globals argument.
  This may also be done statefully by counting the number times an import has been performed, which seems this seems flaky, or by tracking which import has been performed, which seems more concrete.
  Should the origin fall within the overly then the original module is loaded otherwise return the patch.
  Note that a loose check upon the origin allows for substructures within the overlay, strict checks prevent this.
  
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
#   if self.debug : self.log.debug([{arg['__name__']:arg.keys()} if isinstance(arg, dict) else arg for arg in args])
  # Ping
  if (name,self.mapToTarget(name)) in self.mods.keys() :
   if self.debug : self.log.debug("Diverting   : " + name + " -> " + self.mapToTarget(name))
#    if self.debug : self.log.debug("Diverting   : {}".format(self.name + modsep + self.mapToTarget(name)))
   spc = imp.find_module(self.mapToTarget(name), [str(self.root)])
   if self.debug : self.log.debug(spc)
   mod = imp.load_module(name, *spc)
   if self.debug : self.log.debug(mod)
   return mod
  # Pong
  if (self.mapToSource(name),name) in self.mods.keys() :
   if self.debug : self.log.debug("Reverting   : " + self.mapToSource(name) + " <- " + name)
#    return self._import_(self.mapToSource(name), *args, **kvps)
   spc = imp.find_module(self.mapToSource(name))
   if self.debug : self.log.debug(spc)
   mod = imp.load_module(name, *spc)
   if self.debug : self.log.debug(mod)
   return mod
  # Pass through/Catch all 
#   if self.debug : self.log.debug("Returning   : {}".format(name))
  return self._import_(name, *args, **kvps)

 def mapToTarget(self, name) :
  """Maps request to the target module, that is the patch in the overlay"""
  # Converts tiers.package.module to _tiers_._package_._module_
  return modsep.join([self.mask.format(part) for part in name.split(modsep)])

 def mapToSource(self,name) :
  """Maps request to the source module, that is the original module"""
  # Converts _tiers_._package_._module_ to tiers.package.module
  try : 
   mask = self.mask.split("{}")
   source = lambda text : text[(text[:len(mask[0])]==mask[0])*len(mask[0]):len(text)-len(mask[-1])*(text[-len(mask[-1]):]==mask[-1])] # Originally : source = lambda name : name[len(mask[0]):-len(mask[-1])]
   return modsep.join([source(part) for part in name.split(modsep)])
  except AttributeError , error :
   return ""

 def modules(self) : 
  """Lists the overlays implemented within a directory
  
  This method returns a structure mapping the module name to the patches within the overlay.
  Since :class:`Import` needs to track whether or not it is loading the target patch or the source module, one had though that a bidirectional mapping would fit the need.
  `S. Lott`_ explains that this is more of a design error then it is a solution.
  After some thought one realised that the source and target names could be combined into a single key for a dict and that this would suffice for the structure.
  State may then be managed by popping the item, :code:`(source, target)`, from the dict and appending it under the reverse key, :code:`(target, source)`.
  ::
    1) Setup
    mods = {(source, target): path, ...}
    2) Given : source
    path = mods[(mapToTarget(source),source)] = mods.pop((source, mapToTarget(source)))
    3) Given : target
    path = mods.pop((target, mapToSource(target)))

  .. _S. Lott: https://stackoverflow.com/a/1456482/958580
  """
  # This differs from overlays in that it recurses through the 
  # folder structure to find python modules
  ext = '.py'
  mod = lambda parts, ext : [part[:-len(ext)] if enum + 1 == len(parts) else part for enum, part in enumerate(parts)]
  lst = [(mod(file.relative_to(self.root).parts, ext), file) for file in self.root.rglob('*'+ext)]
#   self.log.debug(lst)
  lst = {(self.mapToSource(modsep.join(item[0][:-1])),modsep.join(item[0][:-1])) if item[0][-1] == "__init__" else (self.mapToSource(modsep.join(item[0])),modsep.join(item[0])) : item[1] for item in lst}
  # Originally : lst = {modsep.join(item[0][:-1]) if item[0][-1] == "__init__" else modsep.join(item[0]) : item[1] for item in lst}
  if self.debug : self.log.debug("Overlays    : {}".format(str(lst.keys())))
  return lst 

 def __del__(self):
  """
  This removes ApeMan from :attr:`__builtin__.__import__`, restoring the original import implementation that was in place when ApeMan was instantiated.
  """
  __builtin__.__import__ = self._import_

if __name__ == "__main__" :
 # This simply invokes a demonstration and not any unit tests.
 import subprocess as su
 su.check_output("C:\\Python\\64bit\\2714\\python.exe example27.py", cwd = "e:\\python\\apeman\\mockup") #  shell = True, stderr=su.STDOUT)
