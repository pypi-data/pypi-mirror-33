------
ApeMan
------

This section describes the design and implementation of ApeMan. 
One first considers how the `Ideal Overlay`_ might be structured and work from a user's standpoint before considering the `Ideal Mechanism`_ for implementing this from the developers point.

Ideal Overlay
=============

This and the following sections are discussed with respect to the following project structure.
::

 PROJECT/           # The root folder of ones project
   OVERLAY/         # The folder containing ones overlays
     _PACKAGE_/     # A package that one is pactching
       _MODULE_.py  # A module within the package containing ones patches
     __init__.py    # The file that sets up the ApeMan's OverlayImporter
   __main__.py      # The primary file that one's users would execute 

The structure seems to encompass all of the edge cases one might encounter while implementing an overlay.
It provides various entry points where the the overlay machinery or mechanism may be installed or replace the python machinery.
The :file:`__main__.py` and :file:`OVERLAY/__init__.py` file(s) present the most sensible entry point(s).
The package(s)/module(s) structure is nested to ensure the overlay machinery can handle complex cases.
While the underscored ``PACKAGE`` and ``MODULE`` names prevent namespace clashes under various scenarious.

.. _Apeman:Ideal Import:

Ideal Import
------------

The ideal import statement that would trigger the above overlay of a package or module is illustrated. 

.. code-block :: python
  :caption: __main__.py

  from overlay import PACKAGE
  from PACKAGE import ...

It allows the user to explicitly enable or disable an overlay by ``PACKAGE`` or ``MODULE`` name.
There might even be scope to allow the ``*`` wild card to enable or disable an entire set of overlays within an :file:`OVERLAY`.

A lesser form of this statement might also be possible and is provided for comparison.

.. code-block :: python
   :caption: __main__.py

   import overlay
   from PACKAGE import ...

The user is more restricted by this form and may only enable or disable the complete set of overlays under :file:`OVERLAY`.
 
.. _Apeman:Module Substitution:

Ideal Mechanism
===============

Ideally an overlay should transparenlty substitute the original modules with their patched alternatives.
The following figure shows how this might be implemented. 
The import is to redirected to an overlay which imports and wraps the requested module before returning itself in place of it.

.. The initial import should be redirected to the overlay this performs it's own import of the wrapped module and returns itself in place of it.

.. The initial import should be redircted to import the overlay instead.
   This in turn imports the original module which it wraps. 
   Finally the overlay returns itself in in substitution.

.. _fig:overlay:

.. figure :: .static/figures/overlay.png
   :align: center
   :figwidth: 80%
   
   Ideally an import should be redirected to it's overlay, if any, which imports the original module internally returning itself in replacement. 
   Preferably this should hook into the *Finder* and *Loader* phases of the mechanism.

The Python documentation recommends one intercedes within the the *Impoter* layer and not the *Import* layer. 

Module Substitution
-------------------

One mechanism for effecting overlays is by module swapping. 
If the overlay module being imported could catch the import of the original module being patched one could swap the two modules during an import.

.. topic :: Example : Module Substitution

   Explicitly when one imports the overlay one sets up a trap to catch the import of ``PACKAGE`` from the :file:`__main__.py` 
   
   .. code-block :: python
      :caption: :file:`__main__.py`
      
      import overlay
      import PACKAGE
   
   which maps it to the overlay file, ``overlay/_PACKAGE_.py``. 
   This file is loaded and during its execution it imports the original ``PACKAGE``.
    
   .. code-block :: python
    :caption: overlay/_PACKAGE_.py
   
    from PACKAGE import *
   
   Now the original ``PACKAGE`` is installed as ``_PACKAGE_`` and the overlay as ``PACKAGE``. 
   Later imports will then find and access the overlay in ``sys.modules``.
   While the overlay may access the original under ``_PACKAGE_`` in ``sys.modules``.
 
The :download:`original implementation<34/original.py>` succeeded in implementing this to a degree.
One is under the impression that the import machinery checks that the appropriate module is imported, returning a substitute is quite troublesome to get right.

A more :download:`formal implemetnation <34/substitution.py>` followed shortly afterwards but this too failed to handle nested structures properly.
Getting this right in the *Importer* layer is hampered by the submodule addressing the parent module, which is resolved within the *Import* layer and simply not accessible from a *Finder* or an *Importer*.

The result is that the importer could remap ``MODULE`` to ``OVERLAY._MODULE_`` but could not remap ``PACKAGE.MODULE`` to ``OVERLAY._PACKAGE_._MODULE_`` unless one hooked into *Import* aswell.

.. _Apeman:Module Replacement:

Module Replacement
------------------

.. Module swapping does not appear to be possible within the current (Python 3.4) import API's. 

An alternative to `Module Substitution`_ involves replacing the original module with it's overlay.
Since python provides scoping one may retain a reference to the original module within an overlay and present only the latter to later imports.

This is akin to "hot swapping" modules.
The overlay would replace the original module, within ``sys.modules``, by itself.
Subsequent imports would see the overlay as the default module.
Access to the original module could be acheived via the overlay.

.. .. topic :: Example : Module Replacement

..   When the overlay is loaded it is executed, importing the original module, which is installed in ``sys.modules`` and included in the overlays' scope.
   The overlay is then installed within ``sys.modules``  overwriting the original module.
   Access the original module is now via the overlay. 

The strategy is aggressive and complicates, or probably breaks, some of the import systems features.
Importing sub-package and modules becomes rather tricky and one needs to track what one is importing.
Module reloading is also going to be very tricky as one will have to overwrite both the overlay and the original in quick succession.

.. topic :: Proposed Mechanism

   One means of addressing this is to perform name mangling. 
   Ones main script would import the overlay as usual 
   
   .. code-block :: python
    :caption: :file:`main.py`
   
    import overlay
    import PACKAGE
   
   but the patch would import the mangled variant of the package. 
   One could include preceeding and succeeding underscores to indicate the call is from the overlay.
   
   .. code-block :: python
    :caption: :file:`overlay/_PACKAGE_.py`
   
    from _PACKAGE_ import *
    
   Allowing the importer to see the name ``PACKAGE`` when importing the overlay and ``_PACKAGE_`` when importing the original package/module.
   In this way a custom importer may distinguish between two imports in the sort of bidirectional situation encountered in overlays.

This does not circumvent the underlying problem, however, since ``load_module`` still performs the actual import.
``load_module``, particularly the ``builtin.load_module``, checks for the module in ``sys.modules`` and returns this if it exists, this short circuits anything that one might have done in a customized *Importer*.
In a new session where nothing is loaded this strategy does work since there is no module installed within ``sys.modules``. 
For reloads and sub-package/module access this becomes more tricky as now the root module in the overlay has replaced the original root module.

Practical Mechanisms
====================

.. toctree ::
   :caption: ApeMan Variations
   :name: ApeMan Variations
   :hidden:
   
   Python 3.3 : ApeMan <33/apeman>
   Python 3.4 : ApeMan <34/apeman>
   Python 3.5 : ApeMan <35/apeman>
   Python 3.6 : ApeMan <36/apeman>

Given the previous sections and the various observations one has made it is clear that this is not the simplest thing to implement.
An overlay manager may have to hook into all three entry points in the import mechanism as shown below.

.. figure :: .static/figures/structure/encase.png
   :align: center
   :figwidth: 80%

The remainder of this section discusses the various implementations
   
