# System libraries
import sys
import os
# Sub processes
from subprocess import Popen, PIPE # check_output as cmd, CalledProcessError
# Serialization
import json
# Regular Expressions
import re

def osexec(path, code) :
 """
 This calls a second copy of Python to execute the provided code from the provided path
 """
 # [1] Illustrates pretty printing of json while [2] is more 
 # relevant and illustrates byte to string conversion.
 # 
 # [1] http://stackoverflow.com/a/32093503/958580
 # [2] http://stackoverflow.com/a/25829327/958580
#  print(code.format(*args, **kvps))
 command = Popen([sys.executable,"-c",code], stdout=PIPE, stderr=PIPE, cwd = path)
 output, error = command.communicate()
 if command.returncode == 0 :
#   print("Success")
  output = output.decode('utf-8')
#   print(output)
  try :
   for line in output.split(os.linesep) :
#     print("line : ", line)
    match = re.match("^([\"{].*[\"}])$", line) # "^(\{|\").*(\"|\})$")
    if  match :
#      print(line)
     output = json.loads(line)
     break
  except ValueError : # Python 3 : json.decoder.JSONDecodeError 
   pass
#  reader = codecs.getreader("utf-8") # Remember : import codecs
#  output = reader(output)
  return output
 else : 
  print("Failure")
  regex = """(?:(.*?(?:\r?\n))*)(?P<error>.*): (?P<message>.*?)(?:\r?\n)(?:(.*?(?:\r?\n))*)"""
  regex = re.compile(regex)
  error = error.decode('utf-8')
  print(error)
  match = regex.match(error)
  if match :
   return match.groupdict()
  else :
   return error
