---------
Objective
---------

ApeMans' objective is to achieve the behaviour described in this section; irrespective of Pythons' underlying import implementation.
This is described in three steps the first two describe the necessary package/module structure and the third the expected behaviour.

Site Structure
==============

Consider the following file structure installed within ones site-packages, the simplest accomodated by ApeMan.
:: 

   site-packages/
    overlay/
     __init__.py
     _module_.py
    module.py 

Where the base module has the following content :file:`module.py`,
::

  print("{:40}|{}".format(__file__,__name__))

  class Class() :
   def __str__() :
    return "Class"
    
and the :term:`patch` for the module, :file:`overlay/_module_.py`, has the following content.
::

  print("{:40}|{}".format(__file__,__name__))

  from module import *
  class Class(Class) :
   def __str__() :
    return "Overlay({})".format(super().__str__())
    
and the :term:`overlay`, itself, has the following content within its :file:`overlay/__init__.py`.
::

  print("{:40}|{}".format(__file__,__name__))

  from apeman import ApeMan
  apeman = ApeMan()

Project Structure
=================

Further more consider a simple script one might be working on.
:: 

   PROJECT
    example.py

Where :file:`example.py` has the following contents.
::

  print("{:40}|{}".format(__file__,__name__))

  import overlay
  from module import Class
  print(Class())

Execution
=========
  
Running the code in :file:`PROJECT/example.py` should output the following response.
::
  __main__.py           
  ..\overlay\__init__.py
  ..\overlay\_module_.py
  ..\module.py
  Overlay(Class)

Stepping through its execution should take one through the following sequence of events; the print statements are ignored for brevity :

 :file:`PROJECT/example.py`\ **[3]**\ :code:`import overlay`
   Finds and loads the :mod:`overlay` package executing its :file:`__init__` file and triggering the following actions :
   
   :file:`site-packages/overlay/__init__.py`\ **[3]**\ :code:`from apeman import ApeMan`
     Load the current ApeMan implementation recommended for this version of Python.
     
   :file:`site-packages/overlay/__init__.py`\ **[4]**\ :code:`apeman = ApeMan()`
     Install an instance of :class:`ApeMan` onto the front of :attr:`sys.meta_path`.
     
 :file:`PROJECT/example.py`\ **[4]**\ :code:`import module`
   Import :class:`Class` from :mod:`module` triggering the following actions
   
   :attr:`sys.meta_path[apeman]`
     ApeMan intercepts the search for :mod:`module` and loads :file:`site-packages/overlay/_module_.py` in place of :file:`site-packages/module.py`.
    
     :file:`site-packages/overlay/_module_.py`\ **[3]**\ :code:`from module import *`
       Imports all the objects, or the subset specified by :attr:`__all__`, from the scope of :mod:`module` into its own.

       :attr:`sys.meta_path[apeman]`
         Again ApeMan intercepts the search for :mod:`module` but passes the request on to :attr:`sys.meta_path[SourceFileLoader]` which loads and returns :file:`site-packages/module.py`.

     :file:`site-packages/overlay/_module_.py`\ **[4]**\ :code:`class Class(Class) : ...`
       :class:`module.Class` is now subclassed by and substituted for :class:`overlay._module_.Class` as the module completes it's execution and returns
         
 :file:`PROJECT/example.py`\ **[5]**\ :code:`print(Class())`
   Instantiating :class:`Class` now instantiates :class:`overlay._module_.Class` as opposed to :class:`module.Class` printing "Overlay(Class)" instead of "Class".

.. note ::
 
   The structure described here is implemented within the mockup folder.
   Although the filenames differ and the print statements are removed or substituted by logging calls.
