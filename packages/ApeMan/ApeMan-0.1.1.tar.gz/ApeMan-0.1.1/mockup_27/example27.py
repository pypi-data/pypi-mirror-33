#! python27 
"""
Example 2.7
===========

This module uses the :file:`overlay27` overlay to showcase the use of the :class:`PingPongImport`.
This importer has the very desireably feature that the importer and overlay are distinguished only by the underscores app/prepended to the module name.
"""
import logging; logging.basicConfig(level = logging.DEBUG)
log = logging.getLogger(__name__)
log.debug("Demo.py")
try :
 import overlay27
 from module import Class
 log.debug(Class())
except Exception as error:
 log.debug("\nError : \n" + str(error))