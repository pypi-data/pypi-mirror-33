def stack(logger, items, span = 10) :
 # from apeman.utilities import sliceLists as stack, Indentation
 [logger.debug(items[i:i+span]) for i in range(0, len(items),span)]

class Indentation(object) : 
 """
 The Python 2.7 implementation of :class:`apeman.utils.Indentation`
 """
 
 __indent__ = 0
 __taglen__ = 20
 
 def __init__(self, *args, **kvps) :
  if 'indent' in kvps : self.__indent__ = kvps['indent']
  if 'taglen' in kvps : self.__taglen__ = kvps['taglen'] 

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

