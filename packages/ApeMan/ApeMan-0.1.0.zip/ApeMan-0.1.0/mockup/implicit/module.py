# Python 2.7 Support
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

class Class(object) :

 __name__ = "ClassB"
 
 def __str__(self):
  return ".".join([__name__,self.__name__])