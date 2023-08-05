#!python
"""
Explicit Import
===============

This example uses the following substructure of the mockup structure
::

  mockup/             # Root folder
   explicit/          # The package
    ...               # The explicit package structure
   explicitImport/    # The overlay
    ...               # The patched explicit structure
   module.py          # The source module
   explcitiImport.py  # This file
   
This basically replicates the tests in test.structure.explicit but in a programmer friendly debugging kind of fashion
"""
# from __future__ import print_function
# from __future__ import unicode_literals
# from __future__ import division
# from __future__ import absolute_import
# # import logging; 
# # logging.basicConfig(level = logging.INFO)
# 
# from future import standard_library
# standard_library.install_aliases()
import logging; logging.basicConfig(level = logging.DEBUG)
log = logging.getLogger(__name__)
# Root Module
# ===========
# Ensures that the overlay for the root module is importable
# This roughly checks that tests.structure.testExplicit.testModule/testClassA will succeed
try :
 log.debug("="*10 + " " + "module" + " " + "="*10)
 import explicitImport
 from module import Class
 log.debug(str(Class()))
except Exception as error:
 log.debug("\nError : \n" + str(error))
# Base Module
# ===========
# Ensure that the overlay for a module nested one layer deep is importable
# This roughly checks that tests.structure.testExplicit.testExplicitModule/testClassB will succeed
try :
 log.debug("="*10 + " " + "explicit.module" + " " + "="*10)
 import explicitImport
 from explicit.module import Class
 log.debug(str(Class()))
except Exception as error:
 log.debug("\nError : \n" + str(error))
# Package Import
# ==============
# Ensure that the init file for a package is importable
# This roughly checks that tests.structure.testInit will succeed
try :
 log.debug("="*10 + " " + "explicit.module" + " " + "="*10)
 import explicitImport
 from explicit import __version__
 log.debug(str(__version__))
except Exception as error:
 log.debug("\nError : \n" + str(error))

