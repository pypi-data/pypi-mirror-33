--------
Glossary
--------

.. glossary ::

   :abbr:`API (Advanced Program Interface)` : API
     The interface used by programmers to utilize ones code base.

   :abbr:`FQMN (Fuly Qualified Module name)` : FQMN
     The Fully Qualified Module Name (FQMN) is the complete name of a module or a package e.g. the module name :mod:`PACKAGE.MODULE` and the package name :mod:`PACKAGE`; granted the latter is really a |FQPN|.
  
   :abbr:`FQON(Fuly Qualified Overlay Name)` : FQON
     The Fuly Qualified Overlay Name (FQON) represents the name of an overlay name e.g. the :mod:`OVERLAY` package.
     The name the the user imports to enable a specific suite of patches

   :abbr:`FQPN (Fuly Qualified Package name)` : FQPN
     The Fully Qualified Package Name (FQPN) is the |FQMN| with the module name lobbed off e.g. :mod:`PACKAGE` in :mod:`PACKAGE.MODULE`
  
   :abbr:`FQRN(Fuly Qualified Replacement Name)` : FQRN
     The Fuly Qualified Patch Name (FQPN) represents the name of a particular patch within an overlay e.g. a package, :mod:`OVERLAY._PACKAGE_` or a module, :mod:`OVERLAY._PACKAGE_._MODULE_`

   :abbr:`FQSN(Fuly Qualified Source Name)` : FQSN
     The Fuly Qualified Source Name (FQSN) is the name the package or module being patched within some overlay e.g. the :mod:`PACKAGE.MODULE`.
     This is synonamous with both the |FQPN| and the  |FQMN|

   :abbr:`FQTN(Fuly Qualified Target Name)` : FQTN
     The Fuly Qualified Target Name (FQTN) is the name of the patch within an overlay, taken from the overlays root as though it were a |FQPN| or |FQMN| e.g. the package, :mod:`_PACKAGE_` in :mod:`OVERLAY._PACKAGE_`, or the module, :mod:`_PACKAGE_._MODULE_` in  :mod:`OVERLAY._PACKAGE_._MODULE_`, within an overlay, :mod:`OVERLAY`

   explicit package
     A package that is explicitly identified by the inclusion of an :file:`__init__.py` file.

   implicit package
     A package that is implicitly identified by the inclusion one or more modules, none of which are called :file:`__init__.py`.

   module
     The atomic unit for Python source code e.g. :code:`a` or :code:`c` in :code:`b.c`.
     Traditionally this refers to a python file.
     Within the context of this document it largely excludes :file:`__init__.py` files.

   package
     A collection of one or more modules.
     Traditionally speaking, packages would map to the folders upon ones system; hence any folder containing one or more Python module(s) is a package.
     The package is identified as the first part of a modules' name e.g. :code:`a` and :code:`a.b` in :code:`a.b.c`.

   scaffold
     This refers to the structure of a source package that one is patching.
     This may refer to both the physical structure of the package as it is stored e.g. :file:`package/sub-package/__init__.py` and to the path structure used to import it in python e.g. :mod:`package.sub-package`.
     
   structure
     This refer to the structure of a patch that mimics the scaffold of some source package.
     This may refer to both the physical structure of the patch as it is stored e.g. :file:`OVERLAY/_package_/_sub-package_.py` and to the path structure used to import it in python e.g. :mod:`overlay._package_._sub-package_` or :mod:`package.sub-package`.
     It is implied that the structure of the patch largely mimics the structure of the underlying scaffold.

   submodule
     This refers to any module contained within a package e.g. :code:`b` in :code:`a.b`.

   subpackage
     A package nested within another.
     Traditionally speaking, any subfolder containing a module.
     More accurately the first part of a modules' name, containing more then one part e.g. :code:`a.b` and :code:`a.b.c` in :code:`a.b.c`.

.. rubric:: Footnotes

.. [#fqsn1] This entry is to be deprecated as it is redundant


..   :abbr:`FQON(Fuly Qualified Overlay Name)` : FQON
..     This Fuly Qualified Overlay Name is what is installed i.e. the overlay e.g. :file:`PACKAGE`

..   :abbr:`FQAN(Fuly Qualified Hidden/Abstracted Name)` : FQAN
..     The Fuly Qualified Hidden/Abstracted Name is the module that should have been installed but is now covered up i.e. the original e.g. :file:`_PACKAGE_`

..   :abbr:`FQSN(Fuly Qualified System Name)` : FQSN
..     The Fuly Qualified System Name is what the user really imports e.g. :file:`overlay._PACKAGE_` [#fqsn1]_

..   :abbr:`FQPN(Fuly Qualified Path Name)` : FQPN
..     The Fuly Qualified Path Name is the relative path name e.g. :file:`overlay\\PACKAGE`

..   :abbr:`FQFN(Fuly Qualified Path Name)` : FQFN
..     The Fuly Qualified Path Name is the relative file name (e.g. for a File rather then a Path loader) e.g. :file:`overlay\\PACKAGE\\.__init__.py`

