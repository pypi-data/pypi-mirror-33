"""
Scopes
======

The idea with these tests is along the line of those in the :ref:`Repetition` tests.
Here, however, we are testing the behaviour within a subscope rather then within the same module or within a subpackage.
"""
import sys
from six import PY2, PY3
if PY2 :
 import unittest2 as unittest
 from mock import patch
if PY3 :
 import overlays # This is imported here to enable the patch.module decorator but it might interfere with the tests later, if so switch them to the mockups
 import unittest
 from unittest.mock import patch

# import logging; logging.basicConfig(level = logging.DEBUG)
# import io

class testNestedScope(unittest.TestCase) :
 """
 These tests test the import behaviour under nested scopes e.g. those created by class definitions
 """
 # The original invocation 
 # ::
 #
 #   import overlays
 #   import patlib
 #   class Class() :
 #    import pathlib
 #
 # Yielded the following output, the pathlib entries are the most relevant but the entire log is retained for thoroughness.
 # 
 # DEBUG:apeman:Package (Relative) : apeman
 # DEBUG:apeman:Apeman variant     : Python 3.6
 # DEBUG:apeman.__36__:Initialized : Import
 # DEBUG:apeman.__36__:Overloading : pathlib
 # DEBUG:apeman.__36__:Redirecting : overlays._pathlib_
 # DEBUG:apeman.__36__:Importing   : six
 # DEBUG:apeman.__36__:Importing   : __future__
 # DEBUG:apeman.__36__:Importing   : functools
 # DEBUG:apeman.__36__:Importing   : itertools
 # DEBUG:apeman.__36__:Importing   : operator
 # DEBUG:apeman.__36__:Importing   : sys
 # DEBUG:apeman.__36__:Importing   : types
 # DEBUG:apeman.__36__:Importing   : struct
 # DEBUG:apeman.__36__:Importing   : io
 # DEBUG:apeman.__36__:Importing   : builtins
 # DEBUG:apeman.__36__:Importing   : fnmatch
 # DEBUG:apeman.__36__:Overloading : pathlib
 # DEBUG:apeman.__36__:Importing   : pathlib
 # DEBUG:apeman.__36__:Overloading : pathlib
 # DEBUG:apeman.__36__:Importing   : pathlib
 # DEBUG:apeman.__36__:Importing   : collections
 # DEBUG:apeman.__36__:Importing   : tempfile
 # DEBUG:apeman.__36__:Importing   : functools
 # DEBUG:apeman.__36__:Importing   : warnings
 # DEBUG:apeman.__36__:Importing   : io
 # DEBUG:apeman.__36__:Importing   : os
 # DEBUG:apeman.__36__:Importing   : shutil
 # DEBUG:apeman.__36__:Importing   : os
 # DEBUG:apeman.__36__:Importing   : sys
 # DEBUG:apeman.__36__:Importing   : stat
 # DEBUG:apeman.__36__:Importing   : fnmatch
 # DEBUG:apeman.__36__:Importing   : collections
 # DEBUG:apeman.__36__:Importing   : errno
 # DEBUG:apeman.__36__:Importing   : zlib
 # DEBUG:apeman.__36__:Importing   : bz2
 # DEBUG:apeman.__36__:Importing   : builtins
 # DEBUG:apeman.__36__:Importing   : io
 # DEBUG:apeman.__36__:Importing   : os
 # DEBUG:apeman.__36__:Importing   : warnings
 # DEBUG:apeman.__36__:Importing   : _compression
 # DEBUG:apeman.__36__:Importing   : io
 # DEBUG:apeman.__36__:Importing   : threading
 # DEBUG:apeman.__36__:Importing   : _bz2
 # DEBUG:apeman.__36__:Importing   : lzma
 # DEBUG:apeman.__36__:Importing   : builtins
 # DEBUG:apeman.__36__:Importing   : io
 # DEBUG:apeman.__36__:Importing   : os
 # DEBUG:apeman.__36__:Importing   : _lzma
 # DEBUG:apeman.__36__:Importing   : _lzma
 # DEBUG:apeman.__36__:Importing   : _compression
 # DEBUG:apeman.__36__:Importing   : pwd
 # DEBUG:apeman.__36__:Importing   : grp
 # DEBUG:apeman.__36__:Importing   : nt
 # DEBUG:apeman.__36__:Importing   : builtins
 # DEBUG:apeman.__36__:Importing   : operator
 # DEBUG:apeman.__36__:Importing   : collections
 # DEBUG:apeman.__36__:Importing   : errno
 # DEBUG:apeman.__36__:Importing   : random
 # DEBUG:apeman.__36__:Importing   : warnings
 # DEBUG:apeman.__36__:Importing   : types
 # DEBUG:apeman.__36__:Importing   : math
 # DEBUG:apeman.__36__:Importing   : math
 # DEBUG:apeman.__36__:Importing   : os
 # DEBUG:apeman.__36__:Importing   : _collections_abc
 # DEBUG:apeman.__36__:Importing   : hashlib
 # DEBUG:apeman.__36__:Importing   : _hashlib
 # DEBUG:apeman.__36__:Importing   : _hashlib
 # DEBUG:apeman.__36__:Importing   : _hashlib
 # DEBUG:apeman.__36__:Importing   : _blake2
 # DEBUG:apeman.__36__:Importing   : _sha3
 # DEBUG:apeman.__36__:Importing   : itertools
 # DEBUG:apeman.__36__:Importing   : bisect
 # DEBUG:apeman.__36__:Importing   : _bisect
 # DEBUG:apeman.__36__:Importing   : _random
 # DEBUG:apeman.__36__:Importing   : weakref
 # DEBUG:apeman.__36__:Importing   : _thread
 # DEBUG:apeman.__36__:Importing   : datetime
 # DEBUG:apeman.__36__:Importing   : time
 # DEBUG:apeman.__36__:Importing   : math
 # DEBUG:apeman.__36__:Importing   : _datetime
 # DEBUG:apeman.__36__:Importing   : _datetime
 # DEBUG:apeman.__36__:Importing   : itertools
 # DEBUG:apeman.__36__:Importing   : os
 # DEBUG:apeman.__36__:Importing   : builtins
 # DEBUG:apeman.__36__:Importing   : operator
 # DEBUG:apeman.__36__:Importing   : collections
 # DEBUG:apeman.__36__:Importing   : builtins
 # DEBUG:apeman.__36__:Importing   : operator
 # DEBUG:apeman.__36__:Importing   : collections
 # DEBUG:apeman.__36__:Overloading : pathlib
 # DEBUG:apeman.__36__:Importing   : pathlib
 # DEBUG:apeman.__36__:Importing   : __main__
 # DEBUG:apeman.__36__:Importing   : re

 @patch("sys.modules", sys.modules.copy())
 def testClassScope(self) :
  import pathlib
  class Test() :
   import pathlib
 
if __name__ == "__main__" :
 unittest.main()
 
