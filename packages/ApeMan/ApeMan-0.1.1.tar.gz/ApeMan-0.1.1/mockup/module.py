"""
simple module implementing a single class
"""
# Python 2.7 Support
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

# import logging
# import json
# logging.info(__name__)
# for key, val in sorted(locals().items()) :
#  if key.startswith("__") and key.endswith("__") : 
# #   if key in []:#"__name__", "__file__", "__path__"] : 
# #    logging.info(key, val)
# #   else :
#    logging.info(key)
# from pprint import pprint
# pprint({key:val for key, val in locals().items() if key not in ["__builtins__"]})

class Class(object) :

 __name__ = "ClassA"
 
 def __str__(self):
  # Originally :code:`__package__ + __name__ + self.__name__` was returned but
  # it seems one only needs to return :code:`__name__ + self.__name__` instead
#   return ".".join([__package__ if __package__ else "",__name__,self.__name__])
  # The removes the errant dot that preceeded the name in some tests but not 
  # others e.g. ``.module.Class`` -> ``module.Class``
  return ".".join([__name__,self.__name__])
