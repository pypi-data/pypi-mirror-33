---------
Machinery
---------

:ref:`import:Python's Import Mechanism` provides an overview of the import process.
This section goes into the detail of the machinery operating under the hood.

.. toctree::
  :hidden:
   
   Modules                    <machinery/modules>
   
   Utilities                  <machinery/utilities>


Components
==========

sys.metapath
------------

This is the list of Meta finders that Python systematically checks when looking for a modules specification.

sys.path
--------

This is a list of file paths that Python searches when looking for a module.
I get the impressions that, while this was the go to scanner in Python 2.7, it is now only consulted by the SourceFileLoader from the MetaPath.

sys.modules
-----------

This retains a list of all the loaded modules and is used to return thos that thave already been cached.

Execution
=========

.. graphviz ::
   :caption: Illustration of how simple import is really defined.
   :alt:     Pythons' import command
   :align:   center
   :name:    import command

   digraph {
    subgraph import {
     a;b;
    }
    a [target="_sys.modules", label="sys.modules", target="_top", URL="./import.html#sys-modules"]
    b [target="_Execution",   label="sys.modules", target="_top", URL="./import.html#Execution"]
    a -> b;
   }
   
.. digraph import { "sys.module" [target="_sys.modules"] -> imp [label="sys.module", target="_sys.modules"]}  

.. graphviz ::

   digraph {
    a [shape = "ellipse",   ]
    b [shape = "box",       ]
    c [shape = "circle",    ]
    d [shape = "record",    ]
    e [shape = "plaintext", ]
    a -> b -> c -> d -> e -> a;
    a -> e -> d -> c -> b -> a;
   }

Import
======

.. autofunction :: builtins.__import__

.. autofunction :: importlib.import_module
   
Finders
=======

.. inheritance-diagram :: importlib.abc.Finder importlib.abc.MetaPathFinder importlib.abc.PathEntryFinder

.. inheritance-diagram :: _frozen_importlib_external.FileFinder _frozen_importlib_external.PathFinder _frozen_importlib_external.WindowsRegistryFinder  importlib.machinery.FileFinder importlib.machinery.PathFinder importlib.machinery.WindowsRegistryFinder


.. autoclass :: importlib.abc.Finder
  :members:
  
.. autoclass :: importlib.abc.MetaPathFinder
  :members:
  
.. autoclass :: importlib.abc.PathEntryFinder
  :members:

Loaders
=======

.. inheritance-diagram :: importlib.abc.ExecutionLoader importlib.abc.FileLoader importlib.abc.InspectLoader importlib.abc.Loader importlib.abc.ResourceLoader importlib.abc.SourceLoader
   :parts: 2

.. inheritance-diagram :: _frozen_importlib_external.ExtensionFileLoader _frozen_importlib_external.SourceFileLoader _frozen_importlib_external.SourcelessFileLoader
   :parts: 0

.. autoclass :: _frozen_importlib_external.SourceLoader

.. autoclass :: importlib.abc.FileLoader
  :members:
  :inherited-members:
  :undoc-members:
   
.. autoclass :: importlib.machinery.SourceFileLoader
   
.. autoclass :: importlib.machinery.SourcelessFileLoader
  :members:

Module Specifications
=====================

.. inheritance-diagram:: importlib.machinery.ModuleSpec

.. currentmodule :: importlib.machinery

.. autoclass :: ModuleSpec
  :members:
  :inherited-members:
  :undoc-members:
  
..  .. autoattribute:: ModuleSpec.name

