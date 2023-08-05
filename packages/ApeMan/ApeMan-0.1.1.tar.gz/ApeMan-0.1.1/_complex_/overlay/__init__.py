import importlib
import inspect
import builtins
import os
from pathlib import Path
# Debugging
from pdb import set_trace as db
from pprint import pprint

modsep      = '.'

class OverlayImporter(object):

 def __init__(self, *args, name = None, path = None, root = None, _import_ = __import__, **kvps):
  super().__init__(*args, **kvps)
  self.mask = "{}" # Was "_{}_"
  self.name = name or inspect.getmodule(inspect.stack()[1][0]).__name__
  self.root = Path(root or os.path.dirname(inspect.getmodule(inspect.stack()[1][0]).__file__))
  self.mods = self.modules()
  # Substitutes Import Functionality
  builtins.__import__ = self
  self.imp = _import_
  self.lom = []

 def __call__(self, name, *args) :
  # 
  # Hooks the import statement
  #
  # From the Python Docs we have the arguments for import as 
  # follows :
  #
  #   name   - name - The module name to import
  #   global - glb  - The calling module's global scope
  #   local  - loc  - The calling method's local scope, allows scoped imports
  #   from   - pks  - Referred to as the from list
  #   level  - lvl  - Indicates if the import is local or global
  #
  # Aaron Hall from Stack Overflow [1] describes the arguments
  # as follows for the import statement :
  #
  #  name - The name of the package being imported 
  #  root - The in which one started
  #  vars - The variables in the global use space
  #  subs - The number of levels down that one is e.g. 
  #
  #           from .. import module is 2 sublevels down
  #
  # [1] http://stackoverflow.com/a/37308413/958580
  #
  print(name if args else " - " + name, *[{arg['__name__']:[key for key in arg.keys()if not key.startswith("__") ]} if isinstance(arg, dict) else arg for arg in args])
  if self.mapToTarget(name) in self.mods.keys() :
   if args[2] : # Treates thwe case that there is an import "from" list
#    temp = importlib.import_module(self.name + modsep + self.mapToTarget(name)) # This is a little black magic as we ignore the args and route through a different function
    temp = self.imp(self.name + modsep + self.mapToTarget(name), *args)
#     temp = self.imp(name, *args)
   else :
    temp = {name : importlib.import_module(self.name + modsep + self.mapToTarget(name)) for name in self.stack(name)}
    temp = temp[name.partition(modsep)[0]] # Complex key : temp[self.name + modsep + self.mapToTarget(name.partition(modsep)[0])]
  else :
   temp = self.imp(name, *args)
#   print(temp.__name__,temp.__package__,temp.__file__)
#   print(dir(temp))
  return temp

 def mapToTarget(self, name) :
  """Maps request to the overlay module"""
  # Converts PACKAGE.MODULE to _PACKAGE_._MODULE_ (Originally I thought this mapped to overlay._PACKAGE_._MODULE_)
  return modsep.join([self.mask.format(part) for part in name.split(modsep)])
  
 def modules(self) :
  """ Lists the overlays implemented within a directory """
  ext = '.py'
  mod = lambda parts, ext : [part[:-len(ext)] if enum + 1 == len(parts) else part for enum, part in enumerate(parts)]
  lst = [(mod(file.relative_to(self.root).parts, ext), file) for file in self.root.rglob('*'+ext)]
  return {modsep.join(item[0][:-1]) if item[0][-1] == "__init__" else modsep.join(item[0]) : item[1] for item in lst}

 def stack(self, name) :
  parts = name.split('.')
  return [modsep.join(parts[:i]) for i in range(1,len(parts)+1)]
  
if __name__ == "__main__" :
 import subprocess as su
 su.call(["C:\\Python\\64bit\\342\\python.exe","E:\\Python\\layman\\complex\\__main__.py"])
else :
 OverlayImporter()