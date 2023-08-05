------------
Contribution
------------

Users who come to rely upon ApeMan and wish to request a feature may reach me via e-mail.
Ideally post the question on stack overflow and forward the link or address me in a comment as @carel.

Source Code
===========

The source code is available via git from the location :

 **git@git.manaikan.com:opensource/apeman.git**

Currently pull requests are not allowed as this is a private server but patches are accepted via mail.
In time ApeMan will be moved to either GitLab.com or GitHub.com.

Packaging and Installation
==========================

To package ApeMan one may invoke the build command for a specific ``TARGET``
::

   python setup.py build_TARGET

Persons doing development development are advised to install ApeMan from the repository root using ``pip`` as follows 
::

   pip install -e .

Documentation
=============

The documentation for ApeMan is written in |RST| and compiled using sphinx via the :file:`setup.py` script.
To build the project documentation invoke the following command.
::

   python setup.py build_sphinx

Use the :code:`-h` or :code:`--help` switch to see how this build process may be customized.
   
Testing
=======

Once the repository is setup one may run the ApeMan test suites as follows.
::

   python setup.py test
   
   
.. note ::
   
   Due to the structure of ApeMan and it's dependance upon particular Python versions the test suites will barely succeed or fail catastrophically.
   This is, alas, the expected behaviour at this time.
   One still needs to guard all the tests against the ApeMan implementation, :class:`apeman.OverlayImpoter` or :class:`apeman.Importer`, that is selected in the background.
   This is dependant upon both the Python version and the preferred ApeMan implementation for that version of Python.
   ApeMan was largely developed in Python 3.5 and 3.6 and the tests mostly succed on these platforms.
   Behaviour on other versions of Python will likely fail.
   One is still setting up tox to ensure consistent behaviour upon different versions of Python.

Diagnostics
===========

The following Checks are largely used to understand what the Python import machinery is doing under the hood.
These have not been ratified into unit tests but are noted here for future development.

``__import__``
--------------

It seems that the :attr:`__import__` assigned to :mod:`builtins` is not necessarily the same :meth:`__import__` that is defined in :mod:`importlib`.
This seems to be the case atleast in older CPython (<=2.7 and <=3.3) implementations.
The following script provides the simplest test of this.
::

  import importlib
  import builtins
  print(builtins.__import__ == importlib.__import__)
 
The cause for the discrepency is that the import mechanism in older implementations was implemented in C rather then in Python.
To check if the import in ones system is implemented in Python or in C one may run the following check
::

  import builtins
  import dis
  try :
   dis.dis(builtins.__import__) # Originally : wrapped within a print statement
  except : 
   print("The dis module fails to dissassemble 'builtins.__import__' older versions of Python e.g. 2.7") 
   
An earlier, possibly misplaced invocation that I have also used is as follows.
::

  import inspect
  import importlib
  print(inspect.getsourcelines(importlib.__import__))
