--------------
Module Objects
--------------

Modules are a specialized type that may be invokked as follows
::

 import types
 mod = types.ModuleType()
 

Attributes
==========

The following attributes are assigned to a module when it is instantiated.

``__name__``
 The modules' name, this may be combined with ``__path__`` to determine the FQMN

``__file__``
 Assoscitated source file (If any)

``__doc__``
 Documentation string as is typically found near the top of a file inline with the imports and not nested under a ``if __name__ == '__main__' :`` statement

``__package__``
 The name of the package, that is the FQMP.
 This must be specified to allow relative imports, this is not set when a script is run as is i.e. __name__ == "__main__"

``__path__``
 The path to a package, this might be a .zip/.pyc/.py file for a vanilla package, a directory for a name spaced package or None for a python builtin module.
 Actually this is a list of paths the package will recurse through to find submodules.

``__spec__``
 Module Specification, ths is set up so that the module might be loaded from a spec and a spec might be generated from a module.

Patching Import
===============

A minimal import implementation is provided by David Beasley as follows (David Beaseley @ 1:44)
::

 def load_module(name) :
  # Check mod in sys.modules
  # load = sys.modules.get(name)
  # if load is None :
  exnt = '.py'
  with open(name + extn,'r') as file :
   code = file.read()
  load = type.ModuleType(name)
  load.__file__ = name + extn
  code = compile(code, name + extn, 'exec')
  exec(code, load.__dict__)
  # Register mod in sys.modules and return it
  return load

