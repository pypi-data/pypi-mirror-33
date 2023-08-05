"""
Descriptors
===========
   
This module provides a series of pathlib based descriptors. 
Eventually this should become it's own package, or be included in a more apt one.
"""
# System
from pathlib import Path

class FileName(object) :
 """
 Ensures a file name is stored within the attribute and that 
 it is an instance of Path
 """

 def __get__(self, obj, *args) :
  return self.__filename__

 def __set__(self, obj, val) :
  self.__filename__ = Path(val)

class PathName(object) :
 """
 Ensures a folder name is stored within the attribute and that 
 it is an instance of Path
 """

 def __get__(self, obj, *args) :
  return self.__pathname__

 def __set__(self, obj, val) :
  self.__pathname__ = Path(val)

class RootName(object) :
 """
 Ensures a folder name is stored, converting filenames to paths as necessary
 """

 def __get__(self, obj, *args) :
  return self.__rootname__

 def __set__(self, obj, val) :
  root = Path(val) 
  self.__rootname__ = root.parent if root.is_file() else root

