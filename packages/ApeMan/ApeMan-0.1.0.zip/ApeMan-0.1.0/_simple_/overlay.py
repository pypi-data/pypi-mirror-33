import importlib
import inspect
import builtins
import os
from pathlib import Path

modsep      = '.'

class OverlayImporter(object):

 def __init__(self, *args, path = None, root = None, _import_ = __import__, **kvps):
  """
  """
  super().__init__(*args, **kvps)
  self.mask = "_{}_"
  self.root = Path(root or os.path.dirname(inspect.getmodule(inspect.stack()[1][0]).__file__))
  self.mods = self.modules()
  # Substitutes Import Functionality
  builtins.__import__ = self
  self.imp = _import_
  self.lom = []

 def __call__(self, name, *args) : # (self, *args, *kvps):  
  # Hooks the import statement
  """
  """
  if self.mapToTarget(name) in self.mods.keys() :
   if name in self.lom :
    return self.imp(name, *args)
   self.lom.append(name)
   return importlib.import_module(self.mapToTarget(name)) # This is a little black magic as we ignore the args
  return self.imp(name, *args)

 def mapToTarget(self, name) :
  """
  Maps request to the overlay module
  """
  # Converts PACKAGE.MODULE to overlay._PACKAGE_._MODULE_
  return modsep.join([self.mask.format(part) for part in name.split(modsep)])
  
 def modules(self) : 
  """
  Lists the overlays implemented within a directory
  """
  ext = '.py'
  mod = lambda parts, ext : [part[:-len(ext)] if enum + 1 == len(parts) else part for enum, part in enumerate(parts)]
  lst = [(mod(file.relative_to(self.root).parts, ext), file) for file in self.root.rglob('*'+ext)]
  return {modsep.join(item[0][:-1]) if item[0][-1] == "__init__" else modsep.join(item[0]) : item[1] for item in lst}

