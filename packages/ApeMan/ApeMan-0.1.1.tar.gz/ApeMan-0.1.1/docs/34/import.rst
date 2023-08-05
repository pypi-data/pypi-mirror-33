Import in 3.4
=============

During the migration from Python 3.3 to Python 3.4 a number of API calls were updated, deprecating most of ``imp`` library for ``importlib``.

Inconveniently :func:`importlib.spec_from_module` (or :func:`importlib.spec_from_loader`, I can't remember) seems to have been excluded in this version of python.
Instead it was included in the next version, Python 3.5.

.. note :: API Changes

   Python now calls :func:`imp.find_loader`, which supercedes :func:`imp.find_module`, before calling :func:`imp.load_module`.
   This also saw the introduction of :func:`importlib.find_spec` which introduces the semaphore architecture.


:func:`find_spec`
-----------------

The aim of ``find_spec`` is to return a module specification.
This may be done by calling `machinery.ModuleSpec` directly or by using one of the helper functions.
The helper functions that are provided include ``util.spec_from_file`` and ``util.spec_from_loader``.
The former is very strict about receiving a *file* name, *folder* names are not accepted.
Specifically it will accept a packages' init file e.g. ``.\\PACKAGE\\__init__.py`` or module(s) e.g. ``.\\MODULE.py`` but not package directories e.g. ``.\\PACKAGE`` which excludes namespaced packages.

The :func:`find_spec` function accepts both a module name and possibly a module path.
The module path may be either relative or absolute, while the module path is always absolute. 
The :func:`util.resolve_name` function may be used to convert these arguments into a fully qualified module name (FQMN). 

.. topic :: Example : Standard :func:`find_spec` behaviour

   It is helpful to review how the built in ``find_spec`` responds for different package and module configurations.
   In both cases we are loading a package under the path ``E:\\Python\\overlay\\``.
   
   The first setup represented a traditional package, with an `__init__.py` file, the resulting spec included a loader and the location of this file. 
   The submodule search location listed a single path, though one can supposedly extend this by appending paths to the `__path__` variable within the `__init__.py` file.
   ::
   
      ModuleSpec(name='overlay', 
                 loader=<_frozen_importlib.SourceFileLoader object at 0x0000000001283BA8>, 
                 origin='E:\\Python\\overlay\\__init__.py', 
                 submodule_search_locations=['E:\\Python\\overlay'])
   
   The second setup represented a NameSpaced package, it excluded the `__init__.py` file, resulting spec had no loader and listed it's origin as *namespace*.
   The submodule search location is now a ``_namespace`` object, which has list like properties but prevents popping.
   ::
   
      ModuleSpec(name='overlay', 
                 loader=None, 
                 origin='namespace', 
                 submodule_search_locations=_NamespacePath(['E:\\Python\\overlay']))
   
   Had we been importing a module instead of a package then the `submodule_search_location` attribute would have been empty.
   One does not know how the other attributes would've differed.
