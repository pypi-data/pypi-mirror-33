-------
Overlay
-------

This section describes the best practices for developing ones own overlays.

.. note ::

   This section is still being drafted and one is referred to either the :ref:`index:introduction` and :ref:`objective:Objective` pages.

Structure
=========

Whether ones overlay is made available globally or locally one structures their overlay(s) as follows::

  OVERLAY/        # The root folder of the ApeMan overlay
   _PACKAGE_.py   # The module containing ones patches, renamed after the source module or package
   ...            # Further patches provided by the overlay
   __init__.py    # The file invoking ApeMan; identifying it as an overlay

Importing and invoking :class:`ApeMan` within the overlays' :file:`__init__.py` file ::

  from apeman import ApeMan; 
  apeman = ApeMan()

Local Overlay(s)
================

Locally an overlay may be created within ones project by simply including a folder, :file:`OVERLAY`, and an appropriate :file:`OVERLAY/__init__.py` file invoking ApeMan.
::

 PROJECT/         # The root folder for ones project
  PACKAGE/        # The root folder of ones package.
   OVERLAY/       # The root folder of the ApeMan overlay
    ...           # The contents of the overlay
    __init__.py   # The file invoking ApeMan; identifying it as an overlay
   ...            # The other packages/modules in the package.
   __main__.py    # The main script importing and using the patched module.

Other modules within ones package may then invoke the overlay via relative import.
::

 import .OVERLAY
 from SOURCE import *
 
 ...

Global Overlay(s)
=================

Globally, an overlay, is provided as a separate, standalone package.
::

 PROJECT/         # The root folder for ones project
  OVERLAY/        # The root folder of the ApeMan Overlay
    ...           # The contents of the overlay
   __main__.py    # The main script importing and using the patched module.

In this case the modules in ones package must invoke the overlay using an absolute import.
::

 import OVERLAY
 from SOURCE import *
 
 ...

.. One must explicitly import the features they need as the `OverlayImporter` actually blocks further imports.

.. Note that an overlay package is meant to reside alongside its sibling module to afford the most flexibility. 
.. Whether or not this is possible at every level within a package depends upon how python enforces scoping.
   
Naming
======

It seems conventional upon PyPi to name the packages extending a framework in reference to the framework. 
One there fore recommends that one name any package that depends upon ApeMan as ApeMan-PACKAGE.


.. todo ::

   This section is largely covered by the :ref:`index:Usage` section and should either be merged or deprecated.
   

