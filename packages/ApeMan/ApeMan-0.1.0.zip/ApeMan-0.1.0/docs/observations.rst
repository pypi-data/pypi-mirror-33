------------
Observations
------------

The following observations were not entirely evident from the Python documentation.
These are considered first before discussing the implementation.

Modules
=======

Strictly speaking a :term:`module` is a type, :class:`types.ModuleType`, in Python.

The typical user, however, will understand a module to represnt a python file, that is a file with a :file:`*.py` or :file:`*.pyw` extention, upon their system.

Packages
========

A :term:`package` is a :term:`module`, it too is of type :class:`types.ModuleType` but it will contain one or more sub-package(s) or sub-module(s).

Typically one views a package as a folder upon their system that contains one or more python files or one or more subfolders that evetnually do so.

Naming
======

.. Given a module name, one may map it to any resource, but one may not install it within ``sys.modules`` under an alternate name. 

An overlay patches one module by another with the same name.
Clearly this leads to namespace and scope conflicts and one has to mitigate this in some way.
Two means of ontrolling this include :

 * Renaming the original module, or it's overly, using a unique mapping

 * Enclosing the original module, or it's overlay, within another scope

Experimenting with the Python import mechanism one has learnt that module renaming is not especially easy.

Within the *Importer*, or  *Finder*/*Loader*, layer it does not seem possible to remap a given a module name, ``PACKAGE.MODULE``, to another, ``OVERLAY._PACKAGE_._MODULE_``.
Specifically a *finder*/*importer* in ``sys.meta_path`` can not remap a requested module to an alternate one.
The machinery seems to prevent one from renaming or redirecting an import mid process.
Where this ahppens within the machinery is difficult to pin down as only an :class:`ImportError` is thrown.

It seems possible to perform this mapping by hooking into the *Import* entry point.
In particular one may readily enclose or nest an import. 
Given a module, ``PACKAGE.MODULE``, to import one may redirect this to, ``OVERLAY.PACKAGE.MODULE`` rather easily.

Mapping a module name to an alternate resource is also possible. 
File(s) or folder(s), archives (Zip files) and even URL's are possible resource targets.
That is one may import ``_module_.py`` as the source for ``module`` but may not assign ``module`` as ``_module_`` within `sys.modules` and the *Importer* layer.

Structural Equivalence
======================

.. One may even distribute such a module as a Python package via the Python Package Index, PyPI; ideally, by convention, a separate :file:`setup.py` script would be setup to do this but this is not enforcable.

It is not immediately obvious to a new Python user that a standalone module is simultaneously both importable and executable. 
Any such module must include a guard to distinguish between invocation by import, that is by some other module e.g :code:`import MODULE` or  :code:`from MODULE import ITEM`, and invocation by command line, that is directly through python e.g. :command:`python -m MODULE` or :command:`python MOODULE.py`::

 # Common code that is always executed
 if __name__ == "__main__" :
  # Only executed when invoked from the command line
 if __name__ == "MODULE" :
  # Only executed when invoked from another module
 # Common code that is always executed

A Python project with the simplest possible structure is, therefore, as follows::

  PROJECT/    # Project root folder
   MOUDLE.py  # A standalone module

Equivalently, a structure exists that substitutes the standalone module for a standalone package::

  PROJECT/      # Project root folder
   PACKAGE      # A standalone package
   __init__.py  # Only executed when invoked from another module
   __main__.py  # Only executed when invoked from the command line

When a standalone package is invoked Python elects which file to run, :file:`__init__.py` for invocation by import and :file:`__main__.py` for invocation via command line, negating the need for the guard required in a standalone module.

To Python these two structures are equivalent and they may readily by interchanged.
Packages are comparatively the *descripters* for modules.

Isolation
=========

Python treats each import call as a unique operation. 
It does not pass previously imported modules from the current scope into later import calls. 
The following for example will typically fail 
::

 from tiers import package_a
 from package_a import package_b

while the following, which explicitly identifies the module, will succeed
::

 from tiers import package_a
 from tiers.package_a import package_b

A possible work around could import ``package_b`` from within the init file of ``package_a`` while the latter is being imported. 

.. I do not, however, think that this will work as the import command receives the module name parts as strings and not as references to previous modules.

Effectively imports occur in isolation, are unique from one another and are independent of prior import(s).
The module(s) listed in an ``import`` statement are converted to string arguments before being passed to ``__import__``.
References to previously imported modules are not passed in as is usual within Pythonic.

.. note :: This text is repeated verbatim within the ``tests.testUpperCase.testStructure`` tests, which tests this out every few iterations.

Registration
============

Given that imports occur in Isolation, there is a possibility that one might co-erce an importer to selectively pick and register overlays.
Consider the following overlay structure
::

 PROJECT //      # The project's root folder
  overlay//      # The overlay(s) one wishes to use
   _PACKAGE_.py  # The overlay for PACKAGE 
   _OTHER_.py    # The overlay for some OTHER package
  
In the following lines of code one could make the Meta Path *Finder* register which modules are to be overlayed during the execution of the first line i.e. Importing ``overlay.PACKAGE`` would cause ``PACKAGE`` to be registered and caught in later imports while some ``OTHER`` package would not. 

Python insists on a module object being returned during an import and one may have to install an empty ``type.ModuleType`` into ``sys.modules`` as a place holder, possibly ``None`` is sufficient for this purpose.
Although this is a rather unorthodox, unintuitive and probably not desirable.

The, registered, ``overlay`` would then be caught and imported within later lines. 

::

 from overlay import PACKAGE
 import PACKAGE
 import OTHER

The overlay, ``_PACKAGE_.py`` for the ``PACKAGE``, and the original, ``PACKAGE.py`` for ``PACKAGE``, would both be imported by the overlay importer/manager.
The ``OTHER`` package, by default, would be imported using the usual import mechanism(s).

.. todo :: This section is a bit confusing as it discusses both usage and implementation details. The exact method by which this might finally be implemented is unclear at this time. 

Nuances
=======

This is a collection of notes I'm not entriely sure about.

 * Given a module, :mod:`B`, in a package, :mod:`A`. What is the behaviour when I try to import :mod:`B` from withn :mod:`A.B`.
   This is asked with respect to :meth:`__import__` which accepts both the global and local scope as an argument. 
   One might glean the actual source importing a module through :samp:`{globals}/{locals}["__name__"]` and determine if the overlay is performing the import or some package using the overlay is.
   

References
==========

Even though the import mechanism performs imports in `Isolation`_, passing in strings rather then references to identify a module, it does not prevent one from accessing prior imports.
One may create their own reference to previously imported modules by simply importing them.
This is due to the short circuiting that happens within the import machinery.
For instance, while importing a sub-package or sub-module, one may obtain a reference to any prior module instance, the parent module for example.

This is done best with :func:`importlib.import_module` since :func:`builtins.__import__` tends to suffer from :ref:`side effects <sec:__import__>`.

Errors
======

When debugging an *Importer* or *Finder*/*Loader* combination try to avoid using dictioneries in the initial code. 
Often an import will fail with a ``KeyError`` which does not indicate a fault in ones classes but rather an unassigned key the ``sys.modules``.
e.g. Say one is importing some ``MODULE`` and their importer is still returning ``None`` as it is partially implemented then ``import`` will raise an error as ones code does not install ``module`` in ``sys.modules``.

.. todo :: 

   This is badly explains and simply a kick in the teeth from past me to future me.

.. note :: 

   What I was getting at here is that bad assignments in ``sys.modules`` appear as generic :class:`KeyError`'s which, if one is working with ``dict``'s can lead to some confusion.
   Specifically I was rather frustrated after tracing an error for an entire afternoon that turned out to be rather trivial.
