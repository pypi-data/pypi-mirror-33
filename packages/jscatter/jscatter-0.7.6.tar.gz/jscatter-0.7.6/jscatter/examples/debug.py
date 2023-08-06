# -*- coding: utf-8 -*-
#  this file is intended to used in the debugger
# write a script that calls your function to debug it

import jscatter as js
import numpy as np
import sys
# some arrays
w=np.r_[-100:100]
q=np.r_[0:10:0.1]
x=np.r_[1:10]



q=np.r_[0.001,0.01:0.1:0.01,0.1:15:0.1]

S=js.sf.multiYukawa(q,0.5,0.15,1./np.r_[10,0.5,15],[4.4444,-0.4444,12.4],init0=[-0.01,0.01,0.01])


