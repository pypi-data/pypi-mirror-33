#!/usr/bin/env python
#
# Author: Patrick Hung (patrickh @caltech)
# Author: Mike McKerns (mmckerns @caltech and @uqfoundation)
# Copyright (c) 1997-2016 California Institute of Technology.
# Copyright (c) 2016-2018 The Uncertainty Quantification Foundation.
# License: 3-clause BSD.  The full license text is available at:
#  - https://github.com/uqfoundation/mystic/blob/master/LICENSE
"""
Similar to test_mogi.py

but trying to use scipy's levenberg marquardt.

"""

from test_mogi import *
from scipy.optimize import anneal
import pylab

if __name__ == '__main__':

    lower = array([1000,-1000,0,0])
    upper = array([5000,-0,20,0.5])
    sol = anneal(cost_function, [1000., -500., -10., 0.1], lower=lower, upper=upper, feps=1e-10, dwell=100,T0=10)
    print("scipy solution: %s" % sol[0])
    plot_noisy_data()
    plot_sol(sol[0],'r-')
    pylab.show()

# end of file
