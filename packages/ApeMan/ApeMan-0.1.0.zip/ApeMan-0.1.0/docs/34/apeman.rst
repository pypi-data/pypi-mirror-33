====================
Apeman in Python 3.4
====================

This implementation was really tricky. 
The python documentation at the time was all over the place and referenced three different import implementations.
The final implementation is somewhat of a hack as a result.

.. note :: 

   There are currently four copies of the :file:`__34__.py` file. 
   The :file:`__34__.original.py`, and it's successor :file:`__34__.substitution.py`, file exploit the :ref:`Apeman:Module Substitution` strategy, which fails for nested package structures.
   The :file:`__34__.replacement.py` file supersedes these two files and is considered the `better` implementation but relies upon :ref:`Apeman:Module Replacement`, but it too does not handle nesting.
   Finally :file:`__34__.py` goes full hog and hacks up and replaces the ``builtin.__import__`` method, since the previous cases could not successfully handle nested packages.

.. figure :: ../figures/34/overlay.png
   :align: center
   :figwidth: 80%
   
   The Python 3.4 implementation hooks into the *Import* phase.
   
Ideal Implemetation
-------------------

.. todo :: Merge this with the :ref:`Observations:Isolation` section 

The ideal means of importing a module (See :ref:`Apeman:Ideal Import`) assumes that ``PACKAGE`` is an object (See :ref:`Observations:Isolation`) and that later imports would reference this object in some way. 
Python however performs each import in isolation passing strings and not the objects to subsequent imports (See `Import Isolation`).
Is is possible to access these objects and make subsequent imports rely upon them but this in general not done (See `Import References`).

Import
------

To perform an import one had to drop the underscores in the overlay and monkey patch ``__import__`` with OverlayImporter, a class, rather then a method.

Finders 
-------

Loaders 
-------

The stock loaders provided by python do not seem to allow one to install a module under an alternate name. 
It is possible to load them under an alias however as in 
::

 class IMPORTER :
  def load_module() :
   ...
   temp = LOADER.load_module() # Installs module in sys.modules under LOARDER.name
   sys.modules[ALIAS] = temp   # Installs module in sys.modules under ALIAS

This prevents one from doing things like ``sys.modules[ALIAS] = LOADER.load_module(ALIAS)``, which would be rather convenient.
Actually this generates a ``KeyError`` since ``ALIAS`` and ``LOADER.name`` differ.
The error results from ``LOADER.name`` not being registered within ``sys.modules`` and possibly relates to the built in importers failing to locate ``ALIAS`` within their scope.

The current strategy, although rather radical, involves replacing the registered module with the overlay.
This works because the overlay retains a reference to the original module while the main code pulls in the overlay.

Implementation
--------------

The layer manager in this case simply hooks into the import portion of the import mechanism as is shown in :ref:`import <fig:import>`

.. automodule :: apeman.__34__
   :members:
   :member-order: bysource

