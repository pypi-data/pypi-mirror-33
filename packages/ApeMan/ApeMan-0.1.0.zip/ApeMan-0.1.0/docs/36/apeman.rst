====================
ApeMan in Python 3.6
====================

.. automodule :: apeman.__36__
   :members:
   :member-order: bysource
   :undoc-members:
   :private-members:
   :special-members:

   
.. note::
  
   I recently made a modification the the :meth:`__call__` method for the 3.6 version that should probably be ported to other implementations.
   When sphinx was building the documentation for a module that used apeman, apeman would get installed in the importer list and intercept some of the sphinx imports.
   I think sphinx fiddles with the import statement too and was passing a :obj:`level` key word argument, I have caught such asrguments in :obj:`kvps` but had not passed it through to Pythons import statement, which apeman sets as it's :attr:`self.imp` attribute, that is one was calling :code:`self.imp(name, *args)` instead of :code:`self.imp(name, *args, **kvps)`.

.. oroginally the :obj: roles distinguished between function arguments and variables