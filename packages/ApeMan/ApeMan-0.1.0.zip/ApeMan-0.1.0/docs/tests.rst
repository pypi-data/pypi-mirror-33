-------
Testing
-------

.. toctree::
   :maxdepth: 3
   :hidden:
   :glob:

   Scaffold  <tests/scaffold>
   Structure <tests/structure>

This package deviates slightly from the standard testing pattern.
This is largely due to Python caching previous imports.
Once a module is loaded it persists for the duration of the session/process, so the imports made in one test affect those made in another. 
The `setUp` and `tearDown` functions can not remove imported modules cleanly nor reliably from the cache.
To work around this all the tests are done via sub processes, which ensures a clean cache [#1]_.
The results of each test are returned to the test via json via stdout.

Organization
============

The unit tests are organized into a stack of tiers that each test the existance or implementation of a feature or a set of features.
 
 1. :ref:`tests:Machinery`
 
    These tests are dependant upon the version of Python one is using and determine what functionality is available for the development of ApeMan

 2. :ref:`tests/scaffold:Scaffold`
   
   These tests ensure that the mock structure is importable and usable. 
   Python < 3.3 does not support namespaced packages, per :pep:420, and cannot import the implicit part of the scaffold.
   
 3. :ref:`tests/structure:Structure`
   
    These tests ensure that ApeMan can overlay the scaffold structure with a patched packages and modules.
    It is not imediately obvious but these tests are really meant to ensure overlays may be developed for packages with nesting, that is multi-level packages.
    
 5. :ref:`tests:Repetition`
   
    These tests ensure that repeatedly importing teh same module, that is patched within an overlay, consistently returns the patched module over the original source.
    
 6. :ref:`tests:Stacking`
   
    These, presently unwritten, tests should ensure that the stacking of multiple overlays is possible. 
    That is if one applies one or more overlays that they do not interfere/intercept or bypass one another.
    
 7. :ref:`tests:Rollback`
 
    These tests, originally developed  for :mod:`unittest.mock` from the ApeMan-Overlays, ensure that the original :attr:`builtins.__import__` may be reinstated if ApeMan is removed from ones :attr:`sys.meta_path`.
    
Compatability
=============

:mod:`unittest` in Python 2 provides a subset of the functionality provided in Python 3.
:mod:`unittest2` makes a superset of :mod:`unittest` available to both versions of Python.
Initially one used the following fix to resolve this discrepency ::

  import six
  if six.PY2 :
   import unittest2 as unittest
  if six.PY3 :
   import unittest

As it turns out, however, :mod:`six` provides a cleaner solution ::

  import six
  import unittest

.. The following sections document the tests that are performed.
.. This information is pulled directly from the test source code and may be a bit messy at times.
.. The tests all test an overlay of the `tiers` package, a set of sources that provide a `vanilla` package structure.
.. The reader should know that there is a "vanilla" set of sources called `tiers` which provides a base hierarchy to test the overlays against. 
.. Each overlay monkey patches these sources in some way, where each overlay is described as follows.

.. uppercase
.. =========

.. This Patches the classes in `tiers` to modifying the `__str__` method(s) to print the class name in upper case rather then mixed case. 

.. structure
.. =========

.. This tries out different restructuring techniques within the overlay.
.. .. Potentially one may insert a patch into other NameSpaced packages or even overlay modules within them.
.. For the time being this only explores explicit packages. 
.. .. It should also test restructuring of packages.

.. .. note :: Do not include an init file within the test folder this will probably break things.

.. In theory the code should be listed below but I'm not seeing it at this time.

.. DEPRECATED : See testMachinery
.. .. automodule :: tests.testAssumptions
..    :members:
..    :member-order: bysource

.. automodule :: tests.testExample
   :members:
   :member-order: bysource

.. DEPRECATED : See testMachinery
.. .. automodule :: tests.testFinders
..    :members:
..    :member-order: bysource


Machinery
---------
.. automodule :: tests.machinery
   :members:
   :member-order: bysource

Repetition
----------
.. automodule :: tests.repeats
   :members:
   :member-order: bysource

Stacking
--------

These tests are not implemented yet but should ensure that when importign more then one overlay that each overlay honours eralier overlays.

.. automodule :: tests.rollback
   :members:
   :member-order: bysource

.. rubric:: Footnotes

.. [#1] There is probably some scaling efficiency to be had as a result. 

Notes
-----

Notes about unit testing

 `Selecting <https://stackoverflow.com/a/1068366/958580>` `Tests<http://www.wellho.net/mouth/4446_Combining-tests-into-suites-and-suites-into-bigger-suites-Python-and-unittest.html>`
   This shows how to select tests by deliberately importing them, it might be possible to limit the test surface to only the relevant tests for a Python imlpementation.
   Presently I'm not sure how best to do this in ToX or in unittest.
   
Failure
-------

Python's unittest framework does not create a new session for each test case or suite but runs all of the discovered tests within one session.
ApeMan modifies :attr:`sys.meta_path` and fiddles with the modules in :attr:`sys.modules` while the unit tests for it mess with :attr:`sys.path`. 
This makes testing the ApeMan packages a bit cumbersome.

This section hopes to document some of the odder cases in the hopes that it helps future programmers.

Scaffold
~~~~~~~~
The scaffold tests are known to fail if another test leaves an instance of ApeMan upon :attr:`sys.meta_path`.
After porting ApeMan for Python 2.7 one found that the scaffold tests were failing myteriously.
One could import :mod:`module` from :file:`mockup/module.py` but not any of the submodules :mod:`(explicit.)+module` from :file:`mockup/(explcit/)+module.py`.
It seems that the modules were 
::
  ======================================================================
  ERROR: testPackage (tests.scaffold.testExplicit.TestExample)
  ----------------------------------------------------------------------
  Traceback (most recent call last):
    File "E:\Python\apeman\tests\scaffold\testExplicit.py", line 173, in testPackage
      import package.module
    File "E:\Python\apeman\apeman\__36__.py", line 102, in __call__
      return self._import_(name, *args, **kvps)
    File "package/__init__.py", line 6, in <module>
      ApeMan(name = 'package', root = 'E:\Python\apeman\overlay')
    File "E:\Python\apeman\apeman\__36__.py", line 78, in __init__
      self.mods = self.modules()
    File "E:\Python\apeman\apeman\__36__.py", line 117, in modules
      lst = [(mod(file.relative_to(self.root).parts, ext), file) for file in self.root.rglob('*'+ext)]
    File "E:\Python\apeman\apeman\__36__.py", line 117, in <listcomp>
      lst = [(mod(file.relative_to(self.root).parts, ext), file) for file in self.root.rglob('*'+ext)]
    File "C:\Python\64bit\362\lib\pathlib.py", line 1090, in rglob
      for p in selector.select_from(self):
    File "C:\Python\64bit\362\lib\pathlib.py", line 487, in select_from
      if not is_dir(parent_path):
    File "C:\Python\64bit\362\lib\pathlib.py", line 1326, in is_dir
      return S_ISDIR(self.stat().st_mode)
    File "C:\Python\64bit\362\lib\pathlib.py", line 1136, in stat
      return self._accessor.stat(self)
    File "C:\Python\64bit\362\lib\pathlib.py", line 387, in wrapped
      return strfunc(str(pathobj), *args)
  OSError: [WinError 123] The filename, directory name, or volume label syntax is incorrect: 'E:\\Python\x07peman\\overlay'
These tests must be run directly, :code:`Python -m tests.scaffold.test*`, since unittest does some wierd things to :attr:`sys.path`.
Both :code:`Python -m unittest discover` and :code:`Python -m unittest discover [tests] -t .` fail to run properly as  a result.
Issue `24247 <https://bugs.python.org/issue24247>`_, `23097<https://bugs.python.org/issue23097>`_ and `23882<https://bugs.python.org/issue23882>`_ on the Python bug tracker discuss this but do not appear to offer a workaround or a solution.

