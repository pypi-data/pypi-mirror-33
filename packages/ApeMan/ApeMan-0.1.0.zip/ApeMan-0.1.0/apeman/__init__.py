# Python Compatability
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
# System
import sys
# Logging
# import logging
# log = logging.getLogger(__name__)
import logging; log = logging.getLogger(__name__)
# if __name__ == "__main__":
#  log.basicConfig(level = log.DEBUG)

# Previously this simply imported apeman.py
# ::
#     from .apeman import OverlayImporter
#
# apeman.py would then perform this redirection. 
# To make this work with Python 2.7 the selection code was moved here.
# This largely deprecated the apeman.py file. 
# Later incarnations should provide branches in the Git reposotiry for each version of Python and supply an apeman.py specifci to that version.
# 
if __package__ : # Relative imports for normal usage
 log.debug("Package (Relative) : " + str(__package__))
 if sys.version_info[:2] == (3,6) :
  log.debug("Apeman variant     : Python 3.6")
  from .__36__ import OverlayImporter, Import, version
  ApeMan = Import # OverlayImporter # 
 if sys.version_info[:2] == (3,5) :
  log.debug("Apeman variant     : Python 3.5")
  from .__35__ import OverlayImporter, Import, version
  ApeMan = OverlayImporter
#   ApeMan = Import
 if sys.version_info[:2] == (3,4) :
  log.debug("Apeman variant     : Python 3.4")
  from .__34__ import OverlayImporter, version
  ApeMan = OverlayImporter
 if sys.version_info[:2] == (2,7) :
  log.debug("Apeman variant     : Python 2.7")
  from .__27__ import OverlayImporter, Import, PingPong, version
  ApeMan = OverlayImporter
else : # Absolute imports prevent "SystemError : Parent module '' not loaded,..."
 log.debug("Package (Absolute) : " + str(__package__))
 if sys.version_info[:2] == (3,6) :
  log.debug("Apeman variant      : Python 3.6")
  from __36__ import OverlayImporter, Import, version
  ApeMan = Import
 if sys.version_info[:2] == (3,5) :
  log.debug("Apeman variant      : Python 3.5")
  from __35__ import OverlayImporter, Import, version
#   ApeMan = OverlayImporter
  ApeMan = Import
 if sys.version_info[:2] == (3,4) :
  log.debug("Apeman variant     : Python 3.4")
  from __34__ import OverlayImporter, version
  ApeMan = OverlayImporter
 if sys.version_info[:2] == (2,7) :
  log.debug("Apeman variant     : Python 2.7")
  from apeman.__27__ import OverlayImporter, Import, PingPong, version
  ApeMan = Import # Originally : OverlayImporter
