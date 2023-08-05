# Python 2.7 Support
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import super
from future import standard_library
standard_library.install_aliases()

from explicit.explicit.module import Class

class Class(Class) :

 def __str__(self):
  return super().__str__().upper()