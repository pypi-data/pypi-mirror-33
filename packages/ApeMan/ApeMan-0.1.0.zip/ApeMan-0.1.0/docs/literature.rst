----------
Literature
----------

PEP
===

This section lists the various PEP's that describe the features of the import system.

 :pep:`273` : Zip files
  This discusses how the import system utilizes zipfiles and how one could leverage these in their own code.
 :pep:`302` : *Finders*, *Loaders* and *Importers*
  This discusses the mechanism by which *Finder*, *Loaders* and *Importers* ought to interact, I believe this describes Brett Cannon's conversion from a C to Python based import system.
 :pep:`395` : Qualified Names for Modules (Deprecated)
  Deals with pitfalls in the older import systems
 :pep:`420` : Implicit Namespace Packages
  Identifies the differences between implicit and explicit packages
 :pep:`451` : ModuleSpec
  This discusses the ModuleSpec class implementation
 :pep:`3147` : Module Cache
  This describes the current behaviour of the module cache

Blogs
=====

Since the presentation of "Live and Let Die !" by David Beazley every monkey with a keyboard and a Wordpress account seems to have decided that they are now an authority upon the Python import system.
They are not... and simply clutter the internet. 
Below is a list of more legitimate authorities.

 `Brett Cannon <https://plus.google.com/+BrettCannon>`_ 
   Overhauled the Python import system from versions 3.3 to 3.5 `articles <https://snarky.ca/>`_ are worth a read.

 Nick Coghlan
   Provides a list of `pitfialls <http://python-notes.curiousefficiency.org/en/latest/python_concepts/import_traps.html>`_ in Python's imports and seems to have been the author of author of :pep:395.
   One found this useful during the initial development of ApeMan, but it is bit wishy washy.
   
`Yarbelk <http://stackoverflow.com/a/14050282/958580>`_ and `Sebastian Rittau <http://stackoverflow.com/a/67692/958580>`_ describe some of the changes in the import machinery.

Presentations
=============

This section provides table(s) of contents for the presentations that are available upon the topic.

Live and Let Die !
------------------

David Beazley does a terrific job at covering the import system.

 `Modules`_ 
   Describes the Module type, how it's loaded, compiled and populated.
 `Import`_ 
   Reviews what import really does under the hood.
 `Module Cache`_ 
   Module caching and how it works, intercepting reloads and the like.
 `Import Hooks`_
   Describes the Meta_Path and Path hooks.
 `References`_
   Beazley lists the resources he had used to form his talk. 

.. _`Modules`: https://youtu.be/0oTh1CXRaQ0?t=5820

.. _`Import`: https://youtu.be/0oTh1CXRaQ0?t=6360

.. _`Module Cache`: https://youtu.be/0oTh1CXRaQ0?t=6600

.. _`Import Hooks`: https://youtu.be/0oTh1CXRaQ0?t=8160

.. _`References`: https://youtu.be/0oTh1CXRaQ0?t=10560

.. This serves as a table of contents for the David Beazely video.
.. 
.. ==== ============ ==================================================================================
.. Time Section      Description
.. ---- ------------ ----------------------------------------------------------------------------------
.. 1:37 Module(s)    Describes the Module type, how it's loaded, compiled and populated.
.. 1:43 Import       Reviews what import really does under the hood.
.. 1:50 Module Cache Module caching and how it works, intercepting reloads and the like.
.. 2:16 Import Hooks Describes the Meta_Path and Path hooks.
.. 2:56 References   Beazley lists the resources he had used to form his talk.
.. ..   ..           Brett Cannon talks "How Import Works" and "Import This, That and the Other thing"
.. ==== ============ ==================================================================================

How Import Works
----------------

.. todo ::

   Go through this video again.
   If I remember correctly the fimography was a bit scrappy in this one.

Import This, That and the Other thing
-------------------------------------

.. todo ::

   Go through this video again.

Examples
========

  `"Customizing the Python Import System" by C.W. <http://blog.dowski.com/2008/07/31/customizing-the-python-import-system/>`_
    `blog.dowski.com <blog.dowski.com>`_  (Circa. 2008) seems to provide the first attempt at an online module loader.

  `"Importing Dynamically Generated module (Python Recipe)" by Andars Hammarquist <http://code.activestate.com/recipes/82234-importing-a-dynamically-generated-module/>`_
    The earliest attempt to dynamically import a module  (Circa. 17 Oct. 2001).
    I believe the patch to :mod:`unittest.mock` in the ApeMan-Overlays are a bit more comprehensize then this script.
    
  `PyDev.Debugger <https://github.com/fabioz/PyDev.Debugger/blob/8142cbfbceb1b80e1e118f7fe133d02da7f1f8bd/pydev_import_hook.py#L34>`
    An interesting class I have to still go through this one as I'm not sure how applicable it is or isn't to ApeMan.

Deprecation
===========

.. todo ::

   This belongs elsewhere but one is not entirely sure where to place it just yet.

In the transition from Python 3.3 to Python 3.4 the import machinery got overhauled.
Brett Cannon apparently gutted any remnant C code within these layers and made it all pure Python.
The following table lists what was changed during the transition and lists discrepencies between the standard python library and the code within this package.

This section aims to resolve the function name changes in a quick lookup table. 

================================================ ================================================ ================================================ 
Imp (Python < 3.3)                               Importlib (Python 3.3)                           Importlib (Python > 3.3)
------------------------------------------------ ------------------------------------------------ ------------------------------------------------
`imp.find_module(name[,path])`                   `importlib.find_loader`                          `importlib.util.find_spec(name, package=None)`
`imp.load_module(name, file, path, note)`                                                         `importlib.util.import_module`
================================================ ================================================ ================================================

`note`
 `description` in the python docs, is a small description string for the package.

`path`
 `pathname` in the python docs, is the current file path or possibly the module path.

 
Related 
=======

This section lists a number of related projects that are available upon the Python Package Index

  :PyPI:`aspectlib` and :PyPI:`featuremonkey`
    These seems to be a more advanced implementation of mock or seem tot ackle the problem from some other paradigm.
  :PyPI:`dingus`
    Dingus is a sort of mock object one throws at other code to see what the other code does to it, after an run one post processes the calls made and determines what the object should really do.
  :PyPI:`gorilla`
    This provides a competing method for patching to ApeMan. It seems to register the patches throughout ones code base and apply them when one angers teh Gorilla as it were (Perhaps they dislike the M.. word too ?).
  :PyPI:`recursive-monkey-patch`, :PyPI:`assign`, :PyPI:`pytestutils` and :PyPI:`monkey-patch`
    These packages seem to tackle the problem from a similar side as ApeMan
  :PyPI:`pypatch`
    A more aggressive variant of ApeMan that will actually apply the patch to the source module itself.
  :PyPI:`ook` and :PyPI:`monkey`
    Python, version specific patching, seems to be a nice compliment for use with ApeMan.
  :PyPI:`pyjack`, :PyPI:`monkeypatcher`/:PyPI:`monkeypatch`, :PyPI:`mock-open`, :PyPI:`python-monkey-business` :PyPI:`patched` and :PyPI:`simian`
    These packages appear to do be alternative implementations of :mod:`unittest.mock` (Previously :mod:`mock`)
    Monkeypatcher seems to be dead. 
    PyJack seems to be a well developed competitor to mock.
    Simian and mock-open extend and add functionality to mock.
  :PyPI:`wrapt`
    Graham Dumpleton of WSGI/CGI fame wrote this package as an alternative to :meth:`collections.wraps` it would seem.
  :PyPI:`ext` and :PyPI:`forbiddenfruit`
    This seems to facilitate patching builtins (these are usually written in C and not readily modified from the Python side of things).
  :PyPI:`mr-monkeypatch`
    This supposedly simulates ruby monkey patching but the github page is dead
  :PyPI:`patcher`
    These seem to fall more udner  git-like roll and will diff/patch source trees.
    
    
The following are unrelated but seemed interesting and showed up in a Python search for Patches.

  :PyPI:`whatthepatch`
    More of a diffing tool
  :PyPI:`gorella`
    This has nothing to do with mokey patching modules but rather fixing up regular expressions
  :PyPI:`monkeytime`
    A quicker version of strptime for Python
  :PyPI:`patched_unittest`
    Not sure, seems dead
  :PyPI:`virtualtime`
    Fiddles with the time modules.
  :PyPI:`extras`, :PyPI:`wrappers` and :PyPI:`AnyQt`
    Both provide additional features to the various libraries, it may be possible to provide these as patches for ApeMan-Overlays.
    wrappers seems interesting.
  :PyPI:`pretend`
    It pretends not to be a mock clone but ...
  :PyPI:`modulegraph`
    Python dependency checker that seems to check the compiled bytecode versus the sources.
  :PyPI:`utknows`
    Seems to skip unittests based upon prior executions
  :PyPI:`code_monkey`
    Python refactoring tool
  :PyPI:`patchio`  
    This patches command line applications or something

Totally unrelated

  :PyPI:`ase`
    Check this out, it does sort of co-ordinated molecular model simulation
  :PyPI:`marrie`
    Command line podcast player
  :PyPI:`PyLobby`
    Python chat interface
  :PyPI:`PyDSLtool`
    Easy to program DSL languages
  :PyPI:`agile`
    Metapackage for Python agile development
  :PyPI:`cdiff`
    Coloured diff output, much like a merge tool.
  :PyPI:`overwatch`
    Log watching and tracing/tracking utility.
  :PyPI:`pagoda`
    Simulation framework for Python
  :PyPI:`habito`
    Tracks ones command line usage to measure productivity
  :PyPI:`scd`, :PyPI:`bumpversion` and :PyPI:`versioneer`
    Version number management/tracking
  :PyPI:`Docu`  
    Previously :PyPI:`PyModels` maps Python objects to schemaless databases.
  :PyPI:`IntelHex`
    Binary/hex code editor
  :PyPI:`sphinxcontrib-trio`
    Python/Sphinx extension for Async based documenation
  :PyPI:`gignore`
    Pulls down git ignore files from the github repo hosting them
  :PyPI:`ib_insync` previously :PyPI:`tws_async`
    Some sort of wrapper for some sort of broker interface.
  :PyPI:`pychemy` :PyPI:`tesselate`
    Chemistry related package
  :PyPI:`liable`
    Unittest generator ?
  :PyPI:`pulp-or` and :PyPI:`pulp-py3`
    Linear programming modeller
  :PyPI:`pyaardvark`
    Python USB/PCI interface driver thingamy
  :PyPI:`aperturesynth` and :PyPI:`arches`
    Photographic manipulations
  :PyPI:`todo.py` :PyPI:`tomaty`
    Todo lists
  :PyPI:`mlab`
    Matlab wrapper
  :PyPI:`restview`
    RST viewer, seems interesting
  :PyPI:`apidoc`  
    Documents ones api much like oxygen does
  :PyPI:`curious`
    Graph based data exploration tool
  :PyPI:`planar`
    2D graphics library
  :PyPI:`SciPySim`
    Python simulation package
  :PyPI:`spreadsheet`
    Google/Python API for google sheets
  :PyPI:`hackr`
    Some sort of hackathon assistant
  :PyPI:`snafu`
    Function as a service thingamy, webbased dfunctions ? I'm not sure.
  :PyPI:`askbot` and :PyPI:`askbot-tuanpa`
    SO for django
  :PyPI:`nova6`
    BitTorrent client/search service
  :PyPI:`Literal` 
    Random project
  :PyPI:`coloriffic`
    Determines the base colours in an image
  :PyPI:`towel-foundation`
    DRY Django development
  :PyPI:`soar` :PyPI:`robotframework-httpd`
    Robotics library
  :PyPI:`itermplot`
    Commandline plotting for matplotlib
  :PyPI:`scikit-tensor` :PyPI:`django-matrix-field`
    Multilinear Algebra and Tensor factorizations
  :PyPI:`calibrate`
    Generates callibration curves
  :PyPI:`Alto` and :PyPI:`Django-theming`
  
Media
=====

Known references in Media

 * `The Kinks - ApeMan<https://youtu.be/eEep67akIn4>`_
