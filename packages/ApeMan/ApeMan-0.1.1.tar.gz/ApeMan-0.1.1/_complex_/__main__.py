import overlay

# This file considers various import statements for a package 
# structure. This structure is overlayed by another with the 
# same structure. The set of statements used is controlled by
# the import switch. 
#
switch = 2
#
# [1] Empty FROM list
#
# First set of tests perform import with an empy from list
#
if switch == 1 :
 
  print("\nIMPORT : import tiers\n---------------------\n")
  import tiers
  # print(dir(tiers))
  print("Result : " + tiers.__version__)
  
  print("\nIMPORT : tiers.module_a\n-----------------------\n")
  import tiers.module_a
  print("Result : " + str(tiers.module_a.Class()))
  
  print("\nIMPORT : tiers.package_a\n-----------------------\n")
  import tiers.package_a
  print("Result : " + tiers.package_a.__version__)

# [2] With a FROM list
#
# These tests 
if switch == 2 :

  print("\nIMPORT : import tiers\n---------------------\n")
  import tiers
  print("Result : " + tiers.__version__)
  
  print("\nIMPORT : from tiers import package_a\n------------------------------------\n")
  from tiers import package_a
  print("Result : " + package_a.__version__)
  
  print("\nIMPORT : from tiers import module_a\n-----------------------------------\n")
  from tiers import module_a
  print("Result : " + str(module_a.Class()))
  
  print("\nIMPORT : from tiers.package_a import module_b\n---------------------------------------------\n")
  from tiers.package_a import module_b
  print("Result : " + str(module_b.Class()))
