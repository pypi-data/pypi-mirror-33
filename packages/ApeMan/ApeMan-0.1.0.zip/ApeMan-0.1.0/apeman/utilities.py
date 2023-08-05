"""
Utilities
=========

This module provides common functionality required by other modules within the package.
"""

def sliceLists(logger, items, span = 10) :
 """
 Verbose logging of lists
 
 If a list is particularly long one may find that they can not view the entries of relevance as they are printed beyond the width of the screen. 
 This function cuts the list up into more sensible parts to showing the complete list within a log.
 This is not intended for production but it is usefull enough for development.
 """
 # Makes a list more print friendly
 [logger.debug(items[i:i+span]) for i in range(0, len(items),span)]
  
class Indentation(object) : 
 """Tracks indentation for nested logging messages

 Indented Truncated Messages
 ---------------------------
 
 A utility class providing indented text no longer then a maximum number of characters.
 """
 
 __indent__ = 0
 __taglen__ = 20
 
 def __init__(self, *args, indent = __indent__, taglen = __taglen__ , **kvps) :
  self.__indent__ = indent
  self.__taglen__ = taglen

 def indent(self, label = None, char = " ", length = __taglen__):
  """
  Outputs a message before increasing the increment
  """
  if label :
   message = "{0}{1:{2}}".format(char*self.__indent__, label[:length-self.__indent__], max(length-self.__indent__,1))
  else :
   message = ""
  self.__indent__ += 1
  return message

 def undent(self, label = None, char = " ", length = __taglen__):
  """
  Outputs a message before decreasing the increment
  """
  if label :
   message = "{0}{1:{2}}".format(char*self.__indent__, label[:length-self.__indent__],length-self.__indent__)
  else :
   message = "" 
  self.__indent__ -= 1
  return message

 def ondent(self, label = None, char = " ", length = __taglen__):
  """
  Outputs a message at the current incrementation
  """
  return "{0}{1:{2}}".format(char*self.__indent__, label[:length-self.__indent__],length-self.__indent__)
