--------------------------
Frequently Asked Questions
--------------------------

Overlays
========

Wierd behaviours observed with overlays are documented here for the time being

While importing an overlay ``import`` throws :class:`ReferenceError`
--------------------------------------------------------------------


.. After one has imported an overlay one finds that import throws a :class:`ReferenceError`.
.. This results when, internally, a weak reference is used to point to an :class:`ApeMan` instance.

The most likely cause of this is that you have not retained a reference to the :class:`ApeMan` instance.
You should change the following code in your overlays' init file, :file:`OVERLAY/__init__.py` from
:: 

  from apeman import ApeMan; Apeman ()

to something like the following code.
:: 

  from apeman import ApeMan; apeman = Apeman ()

The reason for this depends upon the implementation of :class:`ApeMan` that you are given when you import it.
Internally the implementation of ApeMan gets selected according to the current Python interpreter and the preferred implementation for that version of Python, either the :class:`Import` or :class:`OverlayImporter` class.
Depending on how the selected class is implemented :attr:`builtins.__import__` may be assigned either a concrete reference or a weak reference to the instance of :class:`ApeMan`.
In the case of a weak reference one must provide their own concrete reference, hence the fix above, to prevent the :class:`ApeMan` instance from being garbage collected when the init code is done executing.
This is a quirk the author monitors with the :mod:`tests.testRollBackWithReference` and :mod:`tests.testRollBackSensReference` tests and hopes to either remove or enforce in due course.

Patch modules versus patch sub-packages
---------------------------------------

As one builds up their suite of patches one may want to substitute a module, providing a patch,
::

  OVERLAY/        # The root folder of the ApeMan overlay
   _PACKAGE_.py   # The module containing ones patches, renamed after the source module or package
   ...            # Further patches provided by the overlay
   __init__.py    # The file invoking ApeMan; identifying it as an overlay

for a sub-package, providing separate patches.
::

  OVERLAY/        # The root folder of the ApeMan overlay
   _PACKAGE_      # The sub-package containing multiple patches, renamed after the source module or package
    ...           # Sub-patches modifying the components of the source module or package
    __init__.py   # The file combining all of these into a single patch
   ...            # Further patches provided by the overlay
   __init__.py    # The file invoking ApeMan; identifying it as an overlay
   
Presently ApeMan does not support this sort of thing; due to it's trapping and substitution mechanism.
The plan is to fix this but for now one must place all of their patched into s single module and may not factor this out into a sub-package.
To be sure this is a decidedly different problem from patching :ref:`faq:Nested Structure(s)`

Nested Structure(s)
-------------------

Given a source package with a heavily nested scaffold
::

  PROJECT/
   PACKAGE/
    SUB-PACKAGE/
     MODULE.py

Apeman, for the most part, supports patching this scaffold with a similarly nested structure.
::

  OVERLAY/
   _PACKAGE_/
    _SUB-PACKAGE_/
     _MODULE_.py



How to ...
==========

Ignore site-packages and environmental variables ?
--------------------------------------------------


One may disable the environmental and site-package when invoking Python as shown in :dabeaz15:`4472`.
This allows one to have "clean" python environment at startup.
::

  python3 -E ...   # Ignore environemnt variables
  python3 -s ...   # Ignore user site-packages
  python3 -I ...   # Combines -E and -s into a single switch

One has seen instructions on how to subsequnelty populate the properly but forgets th reference and the necessary instruction.
