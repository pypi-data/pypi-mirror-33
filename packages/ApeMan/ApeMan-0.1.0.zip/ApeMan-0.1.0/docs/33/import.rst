:orphan:

Import in 3.3
=============

.. The following API changes seem to be necessary

In Python 3.3 the original import mechanism, written in C, was converted to Python.

.. note :: API Changes

   Import calls :func:`imp.find_module` then :func:`imp.load_module` when it imports  a module in this version of Python.
