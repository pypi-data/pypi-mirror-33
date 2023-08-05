-------------------------
Python's Import Mechanism
-------------------------

This section reviews how imports are effected within Python. 
It exists as a compliment to Python's ``imp``/``importlib`` documentation, which I found to be rather terse and a little confusing.
Granted at the time (Circa. 2016) it contained information pertaining to Python 2.7, 3.3, 3.4 and 3.5 all of which saw significant API changes.

The import mechanism is largely a black box. 
Comprising of the core machinery, which one can't really tinker with, and three entry points which one may hook into to a degree.

.. figure :: .static/figures/blackbox.png
   :align:    center
   :figwidth:   80%
   
   Pythons' import mechanism is complex and provides only three entrypoints that one may hook into, *Import* itself or more preferably the *Finder* and/or *Loader* subcomponents.
   
.. The import machinery exists as a black box with three entry points, creating an object that has effect in all three entry points seems like the only way to affect certain behaviours


import determines which module to load and is the first point where one may intercede.
The other, more closely related, points concern finding and loading a package/module.
While one might hook into all three points it is common place, and indeed encouraged, to only hook into the latter two.

.. An object hooking into the latter two points is referred to as an importer, which combines both a loader and a finder into a single object.
   Generally it is not advised to fiddle with the ``__import__`` statement one may readiily 
   Although it is not advised it's possible to monkey patch this function to a degree.
   It is common to have an object behave both as a finder and a loader .
   these are often combined into a single object.


Import
======

`Import <https://docs.python.org/2/reference/simple_stmts.html#import>`_ does a few unexpected things.
It processes ones request before handing over to the machinery and returns the imported module which it, the machinery, loaded.
Both the ``import`` statement, which is parsed and converted into an `__import__`_ call, and the `importlib.import_module`_ function wrap an internal call to `bootstrap.gcd_import` which activates the machinery.

.. _fig:import:

.. figure :: .static/figures/structure/import.png
   :align:   center
   :figwidth:   80%
   
   The import hook may be used to control or alter what gets imported. 
   It is within this hook that one might implement an overlayer manager.

.. _sec:__import__:

``__import__``
--------------

When an import statement is parsed it is converted into a call to ``__import__``.
Calls to ``__import__`` pass either one or five argument(s).
This includes the package/module `name`, the current scopes `global` and `local` variables, a `from` list and a `level`.
The `from` list affects what ``__import__`` returns as follows :

 * If there is no 'from' list it returns the root package e.g. import A, import A.B and import A.B.C all return A.
 
    >>> __import__('tiers', globals(), locals(), [], 0)
    <module 'tiers' from 'E:\\Python\\apeman\\complex\\tiers\\__init__.py'>
    >>> __import__('tiers.module_a', globals(), locals(), [], 0)
    <module 'tiers' from 'E:\\Python\\apeman\\complex\\tiers\\__init__.py'>
    
 * If there is a 'from' list it returns the trunk package e.g. from A.B import C returns A.B.

    >>> __import__('tiers.package_a', globals(), locals(), ('module_a',), 0)
    <module 'tiers.package_a' from 'E:\\Python\\apeman\\complex\\tiers\\package_a\\__init__.py'>

.. The `level` indicates if a relative import is being performed, which is done relative to the package.

.. note :: 

   The sections predating the `__import__`_ section assumed there was no means of intercepting the ``__import__`` mechanism. 
   The problem was viewed from the Importer side of things and the author may have assumed some odd things as a result.

``importlib.import_module``
---------------------------

``importlib.import_module`` allows one to explicitly import a named sub package, this is in contrast to ``__import__``'s behaviour.
.. Using this one may import `A.B.C` versus importing `A` or `A.B`

Finder(s), Loader(s) and Importer(s)
====================================

The machinery splits the work into an independant "finding" and "loading" phases. 
During the "finding" phase the finders/importers in ``sys.meta_path`` are interrogated sequentially to ascertain which one recognizes the requested package or module.
The finder/importer that is familiar with the package or module then returns a loader that it believes can perform the "loading" operation. 
The loader then loads the module and installs it within ``sys.modules``, which it does by executing the source code and updating the ``sys.modules`` dict.

Finder(s)
---------

An object providing a method for determining whether or not it is aware of a *Loader* that might import a given module.

.. figure :: .static/figures/structure/finder.png
   :align:   center
   :figwidth:   80%
   
   The *Finder* returns a *Loader* that Python uses to load a given module. 
   The module is not necessarily specific to the pair.
   Usually they behave more like factory methods loading a selection of modules that are available in a certain format e.g. builtin modules, site-packages and zip based modules.

.. It is meant to returns a suitable *Loader* or ``ModuleSpec`` if it does and ``None`` if it does not.

.. Note       
..
.. These classes are really implemented within _frozen_importlib_external. 
.. The following two lines will generate the inhritance diagram code.
.. import _frozen_importlib_external
.. import importlib
.. ".. inheritance-diagram :: " + \
..     " ".join(["_frozen_importlib_external.{}".format(item) for item in dir(_frozen_importlib_external) if "Finder" in item and item not in [*dir(importlib.abc)]])                                 + "  " + \
..     " ".join(["importlib.abc.{}".format(item)              for item in dir(importlib.abc)              if "Finder" in item and item not in []]) + "  " + \
..     " ".join(["importlib.machinery.{}".format(item)        for item in dir(importlib.machinery)        if "Finder" in item and item not in [*dir(importlib.abc)]])

Loader(s)
---------

An object providing a method that instantiates and registers a module. 

.. figure :: .static/figures/structure/loader.png
   :align:   center
   :figwidth:   80%

   The *Loader* creates, loads, executes, populates and returns a module object.
   These operations allow one some lee-way in how they might alter an import.
   
.. Note       
..
.. These classes are really implemented within _frozen_importlib_external. 
.. The following two lines will generate the inhritance diagram code.
.. import _frozen_importlib_external
..  import importlib
..  ".. inheritance-diagram :: " + \
..      " ".join(["_frozen_importlib_external.{}".format(item) for item in dir(_frozen_importlib_external) if "Loader" in item and item not in [*dir(importlib.abc)]])                                 + "  " + \
..      " ".join(["importlib.abc.{}".format(item)              for item in dir(importlib.abc)              if "Loader" in item and item not in []]) + "  " + \
..      " ".join(["importlib.machinery.{}".format(item)        for item in dir(importlib.machinery)        if "Loader" in item and item not in [*dir(importlib.abc)]])

   
Importer(s)
-----------

.. PEP302 prescribes the use of two different classes, a Finder 
.. and a Loader, that find and load modules respectively. Each 
.. respectively provides a find_module and a load_module method.
.. These two classes can be combined into a unified Importer.

.. The combination of both a *Finder* and a *Loader* into a single class is referred to as an *Importer*.
.. Typically this is done to share state between both operations.

Importers combine the *Finder* and *Loader* into a single object.
They provide a clean mechanism for handling imports since the same class performs both *Finder* and *Loader* operations it can share state information that would normally have to be transferred between the separate operations.

.. figure :: .static/figures/structure/importer.png
   :align:   center
   :figwidth:   80%
   
   Showing the difference between an *Importer* and how it encompases both a *Finder* and a *Loader*.

Since this mechanism has undergone some rather drastic modifications of late the exact mechanism is considered separately for each Python variant.

Module Spec-ification(s)
------------------------

The *Importer* mechanism described above is loosing favour for a semaphore like mechanism, where the *Finder* returns a ``ModuleSpec`` containing an embedded *Loader*.
Any state information that originally would have been stored within an *Importer*, to share it between the *Finder* and *Loader* parts, must now be embedded within a ``ModuleSpec``.
The Python developers believe this allows for a more generic import process.

.. figure :: .static/figures/structure/modspec.png
   :align:   center
   :figwidth:   80%
   
   Module Specifcations assume a semaphor role allowing communication between a finder and loader but do not share a common set of attributes like an *Importer* would.

Old vs. New
===========

With the transition towards ``ModuleSpec`` it becomes harder to combine both the *Loader* and *Finder* into a single **instantiable** *Importer*.
Many of the ``machinery.*Loader`` subclasses expect certain information during their instantiation which is not available during the instantiation of the *Finder*, preventing the instantiation of an *Importer* until this information is known.
The *Finder*, of an *Importer*, must become a factory method which instantiates and returns a *Loader*, hence forming an *Importer*, as required.
The rational for this is that the *Finder*/*Importer* does not need to be instantiated before it's inclusion within ``sys.meta_path``, presumably this is an optimization but it limits the usage of *Importers*.
Effectively this enforces seperate *Finder* and *Loader* classes over an integrated *Importer* class as a result. 

.. This makes the system slightly more modular as the user may specify any one of the available *Loader* classes within the ``ModuleSpec``, but one had to do so with an *Importer* anyways.

One might view this as a step backwards in the API design.
The Python development team seem to think it's an improvement since it accomodates some more obscure import scenarios.
One believes the primary benefit of this stems from providing a module with localized data access.

As an ``imp``/``importlib`` user the *Importer* implementation seems far more structured then the ``ModuleSpec`` one.
The next few sections consider the import mechanism under the respective Python versions.

.. Implementations
.. ===============
.. 
.. The following sub-sections consider the variations of the import mechanism under different versions of Python.
.. These are mostly as commentary to the preceeding section.

.. toctree ::
   :hidden:
   :caption: Python Import Variations
   :name: Import Variations
   
   Python 3.3 : Import <33/import>
   Python 3.4 : Import <34/import>
   Python 3.5 : Import <35/import>

