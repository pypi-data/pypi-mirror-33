from decimal import *

class Decimal(Decimal) :
 def __str__(self) :
  return "D(" + super().__str__() + ")"