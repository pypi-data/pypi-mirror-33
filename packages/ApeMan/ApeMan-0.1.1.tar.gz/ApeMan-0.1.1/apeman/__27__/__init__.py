"""
===================
Python 2.7 : ApeMan
===================

The import mechanism implemented in Python 2.7 is largely written in C and not Python.
It is exposed somewhat through the 
`importlib` was written to correct this afterall.

The Python 2.7 implementation of ${project} is more finnicky as a result.
The code as it stands is a modified version of the 3.3 implementation.

-------------
Compatability
-------------

This section notes the relevant differences between Python 2 and Python 3 that affect this code.

Functions
=========

The argument specifications in Python 2 functions do not support keyword only arguments.
:: 
  def Py2Function(*args,**kvps):
   KEY = kvps['KEY'] if 'KEY' in kvps else VAL
   ...
These were only introduced in Python 3 by PEP 3102.
:: 
  def Py2Function(*args,KEY=VAL,**kvps):
   ...
   
Atleast at the time of writing the above modification seemed necessary.

Implementations
===============

Ironically the best implementation of ApeMan is provided by :mod:`apema.__27__.pingpong`.

.. automodule :: apema.__27__.pingpong

Gotchas
=======

Presently one assigns :attr:`self._import_` within an :class:`Import` during the :meth:`__init__` phase.
This is largely so that the current :attr:`__builtin__.__import__` is used, wherever ApeMan is invoked and not the one that was available when :mod:`apeman` was first loaded.
Globally assigning something like :code:`IMPORT      = builtins.__import__` should be avoided in general.

"""
import six
if six.PY2 : # ToX tries to load these modules in Python3.6 and fails since they are not absolute/relative imports.
 from apeman   import Import, OverlayImporter
 from pingpong import Import as PingPong
version = (0,0,0)