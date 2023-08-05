#!python
"""
Example
=======

This is run against teh following files structure
::

  mockup/        # Root folder
   overlay/      # The overlay
    __init__.py  # The overlay init file invoking ApeMan
    _module_.py  # The target patch 
   module.py     # The source module
   example.py    # This file

"""
# from __future__ import print_function
# from __future__ import unicode_literals
# from __future__ import division
# from __future__ import absolute_import
import logging; 
logging.basicConfig(level = logging.DEBUG)
# 
# from future import standard_library
# standard_library.install_aliases()
import overlay
from module import Class

# print(dir(overlay))
# print(dir(module))

print(Class())

from module import Class
print(Class())
