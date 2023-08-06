import  sys
if sys.version_info>=(3,0):
   from .pyamifex import *
else:
   from  pyamifex import *