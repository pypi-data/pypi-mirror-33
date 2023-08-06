######!/usr/bin/env python
# -*- coding: utf-8 -*-

# Do divisions with Reals, not with integers
# Must be at the beginning of the file
from __future__ import division
from __future__ import print_function

# Import necessary Python modules
modulesNames = ['sys', 'math', 'warnings', 'copy']
for module in modulesNames:
	try:
		# because we want to import using a variable, do it this way
		module_obj = __import__(module)
		# create a global object containging our module
		globals()[module] = module_obj
	except ImportError:
		#sys.exit(u"ERROR : Module " + module + " not present. \n\n Please, install it \
		raise ImportError(u"ERROR : Module " + module + " not present. \n\n Please, install it \
			      \n\n Edit the source code for more information")
from shutil import copyfile
try:
	import numpy as np                               # need version 1.7 or higher
	from numpy.random import normal,randint
except ImportError:
	raise ImportError(u"ERROR : Module Numpy not present. \n\n Please, install it \
		      \n\n Edit the source code for more information")
try:
	import os
	from os import path, access, R_OK, mkdir         # W_OK for write permission.
except ImportError:
	raise ImportError("ERROR : Module os not present. \n\n Please, install it \
		      \n\n Edit the source code for more information")
try:
	import scipy as sp                               # need version 0.12 or higher
except ImportError:
	raise ImportError(u"ERROR : Module scipy not present. \n\n Please, install it \
		      \n\n Edit the source code for more information")
try:
	import matplotlib.pyplot as plt                  # module to plot figures
	from matplotlib import cm
	from matplotlib.patches import Polygon
except ImportError:
	raise ImportError(u"ERROR : Module matplotlib not present. \n\n Please, install it \
		      \n\n Edit the source code for more information")
try:
	from pylab import savefig                        # Module to manage figures
except ImportError:
	raise ImportError(u"ERROR : Module pylab not present. \n\n Please, install it \
		      \n\n Edit the source code for more information")
try:
	from kapteyn import kmpfit
except ImportError:
	raise ImportError(u"ERROR : Module kapteyn not present. \n\n Please, install it \
		      \n\n Edit the source code for more information")

# Definition of functions

def model(p, x):
	"""
	Define the model
	Here, this is a linear model y = a + b*x
	"""
	a, b = p
	return a + b*x

def residuals(p, data):
	"""
	Residuals function for data with errors in both coordinates
	"""
	a, b = p
	x, y, ex, ey = data
	w = ey*ey + ex*ex*b*b
	wi = np.sqrt(np.where(w==0.0, 0.0, 1.0/(w)))
	d = wi*(y-model(p,x))
	return d

def residuals2(p, data):
	"""
	Residuals function for data with errors in y only
	"""
	a, b = p
	x, y, ey = data
	wi = np.where(ey==0.0, 0.0, 1.0/ey)
	d = wi*(y-model(p,x))
	return d
  
def williamson(x, y, errx, erry, struct, myoutput):
	"""
	Compute Williamson
	"""
	
	if struct[3] != 0 and struct[3] != None:
		if struct[1] != 0 and struct[1] != None:
			ui = errx**2
			vi = erry**2
		else:
			ui = 1.
			vi = erry**2
	else:
		ui = 1.
		vi = 1.
	w = np.where(erry==0.0, 0.0, 1.0/(erry*erry))
	a,b = lingres(x, y, w)
	beta = myoutput.beta
	#a,b = beta0
	a_y = a; b_y = b
	
	n = 0 
	cont = True
	while cont:
		# Step 2: Use this slope to find weighting for each point
		wi = (vi+b*b*ui)**-1
		# Step 3: Calcu;ate weighted avarages
		w_sum = wi.sum()
		x_av = (wi*x).sum() / w_sum
		x_diff = x - x_av
		y_av = (wi*y).sum() / w_sum
		y_diff = y - y_av
		# Step 4: Calculate the 'improvement' vector zi
		zi = wi*(vi*x_diff + b*ui*y_diff)
		b_will = (wi*zi*y_diff).sum()/ (wi*zi*x_diff).sum()
		cont = abs(b-b_will) > 1e-12 and n < 100
		n += 1
		b = b_will

	#print "average x weighted, unweighted:", x_av, x.mean()
	# Step 5: Repeat steps 2-4 until convergence
	# Step 6: Calculate 'a' using the averages of a and y
	a_will = y_av - b_will*x_av 
	# Step 7: The variances
	wi = (vi+b_will*b_will*ui)**-1
	w_sum = wi.sum()
	z_av = (wi*zi).sum() / w_sum
	zi2 = zi - z_av
	Q =1.0/(wi*(x_diff*y_diff/b_will + 4*zi2*(zi-x_diff))).sum()
	sigb2 = Q*Q * (wi*wi*(x_diff**2*vi+y_diff**2*ui)).sum()
	siga2 = 1.0/w_sum + 2*(x_av+2*z_av)*z_av*Q + (x_av+2*z_av)**2*sigb2
	siga = np.sqrt(siga2)
	sigb = np.sqrt(sigb2)
	
	return a_will, b_will, siga, sigb, beta, x_av, x.mean()


def confidence_band(x, dfdp, confprob, fitobj, f, abswei=False):
	"""
	 Given a value for x, calculate the error df in y = model(p,x)
	 This function returns for each x in a NumPy array, the
	 upper and lower value of the confidence interval. 
	 The arrays with limits are returned and can be used to
	 plot confidence bands.  
	 
	 Input:
	 x        NumPy array with values for which you want
	          the confidence interval.
	 dfdp     A list with derivatives. There are as many entries in
	          this list as there are parameters in your model.
	 confprob Confidence probability in percent (e.g. 90% or 95%).
	          From this number we derive the confidence level 
	          (e.g. 0.05). The Confidence Band
	          is a 100*(1-alpha)% band. This implies
	          that for a given value of x the probability that
	          the 'true' value of f falls within these limits is
	          100*(1-alpha)%.
	 fitobj   The Fitter object from a fit with kmpfit
	 f        A function that returns a value y = f(p,x)
	          p are the best-fit parameters and x is a NumPy array
	          with values of x for which you want the confidence interval.
	 abswei   Are the weights absolute? For absolute weights we take
	          unscaled covariance matrix elements in our calculations.
	          For unit weighting (i.e. unweighted) and relative 
	          weighting, we scale the covariance matrix elements with 
	          the value of the reduced chi squared.
	
	Returns:
	y          The model values at x: y = f(p,x)
	upperband  The upper confidence limits
	lowerband  The lower confidence limits   
	
	Note:
	If parameters were fixed in the fit, the corresponding 
	error is 0 and there is no contribution to the condidence
	interval.
	"""  
	
	from scipy.stats import t
	
	# Given the confidence probability confprob = 100(1-alpha)
	# we derive for alpha: alpha = 1 - confprob/100 
	alpha = 1 - confprob/100.0
	prb = 1.0 - alpha/2
	tval = t.ppf(prb, fitobj.dof)
   
	C = fitobj.covar
	n = len(fitobj.params)              # Number of parameters from covariance matrix
	p = fitobj.params
	N = len(x)
	if abswei:
		covscale = 1.0
	else:
		covscale = fitobj.rchi2_min
	df2 = np.zeros(N)
	for j in range(n):
		for k in range(n):
			df2 += dfdp[j]*dfdp[k]*C[j,k]
	df = np.sqrt(fitobj.rchi2_min*df2)
	y = f(p, x)
	delta = tval * df   
	upperband = y + delta
	lowerband = y - delta 
	
	return y, upperband, lowerband
	  

def lingres(xa, ya, w):
	"""
	Return a, b for the relation y = a + b*x
	given data in xa, ya and weights in w
	"""

	sum   =  w.sum()
	sumX  = (w*xa).sum()
	sumY  = (w*ya).sum()
	sumX2 = (w*xa*xa).sum()
	sumY2 = (w*ya*ya).sum()
	sumXY = (w*xa*ya).sum()
	delta = sum * sumX2 - sumX * sumX 
	a = (sumX2*sumY - sumX*sumXY) / delta
	b = (sumXY*sum - sumX*sumY) / delta
	
	return a, b

class color:
	"""
	Class for bold/colors fonts in texts
	"""
	PURPLE = u'\033[95m'
	CYAN = u'\033[96m'
	DARKCYAN = u'\033[36m'
	BLUE = u'\033[94m'
	GREEN = u'\033[92m'
	YELLOW = u'\033[93m'
	RED = u'\033[91m'
	BOLD = u'\033[1m'
	IT = u'\x1B[3m'
	UNDERLINE = u'\033[4m'
	END = u'\033[0m'
	#print color.BOLD + u'Hello World !' + color.END