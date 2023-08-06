######!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
##########################################################
#                                                        #  
#            Age-Elevation profile script                #
#                                                        #  
#                 By Xavier Robert                       #
#                Grenoble, 16/03/02                      #
#                   Lima, 18/01/10                       #
#                                                        #  
##########################################################


 This code is to compute regressions for points with their error
      using different regression methods


"""
# Do divisions with Reals, not with integers
# Must be at the beginning of the file
from __future__ import division
from __future__ import absolute_import
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
	from scipy.odr import Data, Model, ODR, RealData, odr_stop
except ImportError:
	raise ImportError(u"ERROR : Module scipy not present. \n\n Please, install it \
		      \n\n Edit the source code for more information")
try:
	import matplotlib.pyplot as plt                  # module to plot figures
	from matplotlib import cm
	from matplotlib.patches import Polygon
	from matplotlib import rc
except ImportError:
	raise ImportError(u"ERROR : Module matplotlib not present. \n\n Please, install it \
		      \n\n Edit the source code for more information")
try:
	from pylab import savefig                        # Module to manage figures
except ImportError:
	raise ImportError(u"ERROR : Module pylab not present. \n\n Please, install it \
		      \n\n Edit the source code for more information")
try:
	from collections import OrderedDict
except ImportError:
	raise ImportError(u"ERROR : Module collections not present. \n\n Please, install it \
		      \n\n Edit the source code for more information")
try:
	from kapteyn import kmpfit
except ImportError:
	raise ImportError(u"ERROR : Module kapteyn not present. \n\n Please, install it \
		      \n\n Edit the source code for more information")


# Import specific modules
from .statsfuncs import *


############################################################################
############################################################################

#def plotgraphreg(frame, struct, x, y, errx, erry, X, Y, 
def plotgraphreg(struct, x, y, errx, erry, cpt,
                 labeldata, statstypes, a_will, b_will, 
                 verts, confprob, 
                 fitobj, fitobj2, fitobj3):
	
	"""
	Function to plot data and regression stats
	
	USAGE
		axes = plotgraphreg(struct, x, y, errx, erry, colors,
		                    labeldata, statstypes, a_will, b_will, 
		                    verts, confprob, fitobj, fitobj2, fitobj3)
		                    
	INPUT
		1. struct: structure of the data we want to plot
		
		2. x, y: x and y data to plot
		         x and y should be vectors with the same length
		      
		3. errx, erry: errors in x and y respectively.
				       errx and erry should be vectors with the same lenght than x and y
		
		4. cpt: color to plot
		
		5. labeldata: string to be used in the legend of the data

		6. statstypes: Type(s) of the stats to plot
			  		   0 = kmpfit effective variance
					   1 = kmpfit unweighted
					   2 = Williamson
					   3 = Cl relative weighting in X &/or Y
					   ex: statstype = [0,1,2,3] (Default)
						   statstype = [1,3]
						
		7. a_will, b_will: output from the stats models
		
		8. verts: confidence enveloppe
		
		9. confprob: the confidence interval probabilty (in %)

		10. fitobj, fitobj2, fitobj3: Results of the data fitting for each method used
		
	OUTPUT
		axes: axes of the graph
	
	"""
	colorsdict = {'b'          : 'c',
	              'darkorange' : 'orange', 
	              'green'      : 'lightgreen',
	              'peru'       : 'burlywood',
	              'black'      : 'silver',
	              'darkviolet' : 'violet'}
	pointdict = {'b'          : 'o',
	             'darkorange' : 's', 
	             'green'      : 'v',
	             'peru'       : 'p',
	             'black'      : 'h',
	             'darkviolet' : 'd'}
	# Plot the data and the least squared weigthed model 
	#      depending if we have errors on X/Y or only Y
	if struct[1] != 0 and struct[1] != None:
		if struct[3] != 0 and struct[3] != None:
			#plt.errorbar(y, x, xerr=erry, yerr=errx,  fmt='o', label=labeldata)
			plt.errorbar(y, x, xerr=erry, yerr=errx, c=cpt,  fmt=pointdict[cpt], label=labeldata)
			if 0 in statstypes:
				#plt.plot(model(fitobj.params,X), X, 'g', ls='--', lw=2, label=u"kmpfit effective variance")
				plt.plot(model(fitobj.params,x), x, 'g', ls='--', lw=2, label=u"kmpfit effective variance")
		else:
			frame.errorbar(y, x, xerr=erry, c=cpt,  fmt=pointdict[cpt], label=labeldata)
			if 0 in statstypes:
				#plt.plot(model(fitobj2.params,X), X, 'g', label=u"kmpfit errors in y only")
				plt.plot(model(fitobj2.params,x), x, 'g', label=u"kmpfit errors in y only")
	else:
		frame.plot(y, x, fmt = pointdict[cpt], label=labeldata)
	# Plot the classic regression
	if 1 in statstypes:
		#plt.plot(model(fitobj3.params,X), X, 'r', label=u"kmpfit unweighted")
		plt.plot(model(fitobj3.params,x), x, 'r', label=u"kmpfit unweighted")
	# Plot the Williamson regression
	if 2 in statstypes:
		#plt.plot(model((a_will,b_will),X), X, 'y', label=u"Williamson")
		plt.plot(model((a_will,b_will),x), x, 'y', label=u"Williamson")
	if struct[3] != 0 and struct[3] != None and 3 in statstypes:
		# plot the confidence intervals
		#poly = Polygon(verts, closed=True, fc='c', ec='c', alpha=0.15, #ls = 'dashed',
		poly = Polygon(verts, closed=True, fc=colorsdict[cpt], ec=colorsdict[cpt], alpha=0.2, #ls = 'dashed',
		           label="CI (" + str(confprob) + u"%) relative weighting in X & Y")
		axes = plt.gca()
		axes.add_patch(poly)
	
	#return frame, axes
	return axes

	
############################################################################

def vertprofile(datafnme = (u'',), work_dir = (u'',),  header = (1,), struct = ([1,2,3,4],),
	labelx = u'to be completed', labely = u'to be completed', labeldata = (u'Data',),
	rangex = None, rangey = None,
	statstypes = [0,1,2,3], confprob = 95.0,
	fontsz = 10, fontleg = 9,
	output = 'graph'):

	"""
	This code is to compute regressions for points with their error
      using different regression methods
	
	USAGE
		>>>from vertprof import vertprofile
		>>>vertprofile(datafnme = u'', work_dir = u'',  header = 1, struct = [1,2,3,4],
						labelx = 'to be completed', labely = 'to be completed', rangex = None, rangey = None,
						statstypes = [0,1,2,3], confprob = 95.0,
						fontsz = 10, fontleg = 9,
						output = 'graph')
		
	INPUTS
		To use options or inputs, you need to set them as
		vertprof(option_name = option_value, [...])
	
		1. work_dir: tuple (i.e. (u'data1 workdir',u'data2 workdir',...) of the Working directory(-ies) (local path)
		             for each dataset
				ex: work_dir = (u'Purgatorio3/',) (note the (,) structure if there is only one dataset to plot
				Default None
		2. datafnme: tuple (i.e. (u'data1 name ',u'data2 name',...) of the name(s) of text data file
	           should be in the form : Alt - Age - Age_Error
				ex: datafnme = 'Purgatorio3.txt'
		3. header: tuple of the number of lines of the header in the data for each dataset
				ex: header = (1,) (Default)
		4. struct: tuple of the structure of the data for each dataset
	         Struct = ([Xdata, Xerr, Ydata, Yerr],)
	         where Xdata, Xerr, Ydata, Yerr give their respective columns in the data file
	         If one of the data type do not exist, set the corresponding column to NONE
			ex : struct = ([1,2,3,4],) (Default)
		5. output: name of output
				ex: output = 'graph' (Default)
		6. labelx/labely: label x-axis/y-axis
				ex: labelx = 'Exposure age (ka)'
					labely ='Distance to the top of the scarp (m)'
		7. labeldata: tuple (i.e. (u'data1 label',u'data2 label',...) with the name of the type of data
		              for each dataset plotted
		              default = (u'Data',)
		8. rangex/rangey: Set the x- and y-range
	               Depends on type of data
					ex: rangex = [0,8]
						rangey = [10,4] (in that case, the axis is inverted)
		9. statstypes: Type(s) of the stats to plot
					0 = kmpfit effective variance
					1 = kmpfit unweighted
					2 = Williamson
					3 = Cl relative weighting in X &/or Y
					ex: statstype = [0,1,2,3] (Default)
						statstype = [1,3]
		10. fontsz: labels fontsize
				ex: fontsz = 10 (Default)
		11. fontleg: legend fontsize
				ex: fontleg = 9 (Default)
		12. confprob: the confidence interval probabilty (in %)
				ex: confprob = 95.0 (Default)

	OUTPUTS
		For each dataset, the module outputs a pdf graph, and a text file with the stats outputs for each method asked
	
	CONTACT
		If needed, do not hesitate to contact the author. 
		Please, use https://isterre.fr/spip.php?page=contact&id_auteur=303

	LICENCE
		This package is licenced with `CCby-nc-sa` (https://creativecommons.org/licenses/by-nc-sa/2.0/)
	"""
	
	# set colors
	# For the moment, only for 6 datasets, it should be enough
	colors = ['b', 'darkorange', 'peru', 'black', 'darkviolet', 'green']
	
	# initiate variables
	erry = errx = a_will = b_will = verts = fitobj = fitobj2 = fitobj3 = None
	# Tuples to lists
	datafnme = list(datafnme)
	work_dir = list(work_dir)
	header = list(header)
	struct = list(struct)
	labeldata = list(labeldata)
	
	# Initiate the plotting
	plt.rc(u'font', size = fontsz)
	#plt.rc(u'title', size = fontsz)
	plt.rc(u'legend', fontsize = fontleg)
	# Open figure
	plt.figure(1).clear
	#plt.add_subplot(1,1,1, aspect=1, adjustable=u'datalim')
	
	# If the minima input data are not given print the help file
	if not datafnme: 
		help(vertprofile)
		raise TypeError(color.RED + u'ERROR : ' + color.END + u'Name of Input file not given...')

	# check if the length of work_dir, struct and labeldata are equal to the length of datafnme
	# If not, copy the first record to the others, with a warning
	for item in [work_dir, header, struct, labeldata]:
		if len(datafnme) != len(item): 
			warnings.warn(color.YELLOW + u"\nWARNING : " 
			              + color.END + u"work_dir, header, struct and/or labeldata may be the same for all dataset")
			#item = (item[0])
			for i_data in range (1, len(datafnme)):
				item = item.append(item[0])
				#item[i_data] = item[0]
			
	# do a loop on the number of dataset to plot
	for i_data in range (0, len(datafnme)):
		# check if the working directory exists, if not, create it
		if work_dir[i_data].strip():
			if work_dir[i_data][-1:] != u'/': work_dir[i_data] = work_dir[i_data] + u'/'
			if path.exists(work_dir[i_data]) == False:
				os.mkdir(work_dir[i_data])
			else:
				warnings.warn(color.YELLOW + u"\nWARNING : " + color.END + u"Working directory already exists and will be erased\n")
			# Check if the file exists in the main folder
			#       if not, ckeck in the working folder
			#          if only in the working folder, copy it to the main folder
			if not path.isfile(datafnme[i_data]):
				if not path.isfile(work_dir[i_data] + datafnme[i_data]):
					#sys.exit(color.RED + u"ERROR : " + color.END + u"Input file %s does not exist..." % datafnme)
					raise NameError(color.RED + u"ERROR : " + color.END + u"Input file %s does not exist..." % datafnme[i_data])
				else:
					copyfile(work_dir[i_data] + datafnme[i_data], datafnme[i_data])	
			if not path.isfile(work_dir[i_data] + datafnme[i_data]):
				copyfile(datafnme[i_data], work_dir[i_data] + datafnme[i_data])
			datapath = work_dir[i_data] + datafnme[i_data]
		else:
			if not path.isfile(work_dir[i_data] + datafnme[i_data]):
				#sys.exit(color.RED + u"ERROR : " + color.END + u"Input file %s does not exist..." % datafnme)
				raise NameError(color.RED + u"ERROR : " + color.END + u"Input file %s does not exist..." % datafnme[i_data])
			else:
				datapath = datafnme[i_data]
				work_dir[i_data] = u''
		
		# read data
		data = np.loadtxt(datapath, skiprows = header[i_data])
		
		y = data[:,struct[i_data][0]-1]
		if struct[i_data][1] != 0 and struct[i_data][1] != None:
			erry = data[:,struct[i_data][1]-1]
		else:
			erry = 0
		x = data[:,struct[i_data][2]-1]
		if struct[i_data][3] != 0 and struct[i_data][3] != None:
			errx = data[:,struct[i_data][3]-1]
		else:
			errx = 0
		N = len(x)
	
		# Open new file to print the results
		f1w = open(work_dir[i_data] + u'results_' + datafnme[i_data], 'w')
		string = ' '
		print(string); f1w.write(string + u"\n")
		string = ' '
		print(string); f1w.write(string + u"\n")
		string = ' '
		print(string); f1w.write(string + u"\n")
		string = u'             Dataset ' + labeldata[i_data]
		print(color.RED + color.BOLD + string + color.END); f1w.write(string + u"\n")
		string = u"Results of weigthed least square from file " + datafnme[i_data] + u"\n"
		print(color.RED + color.BOLD + string + color.END); f1w.write(string + u"\n")
		string = u"xmax/min = " + str(x.max()) + u", " + str(x.min())
		print(string); f1w.write(string + u"\n")
		string = u"ymax/min = " + str(y.max()) + u", " + str(y.min())
		print(string); f1w.write(string + u"\n")
		string = u"x/y mean = " + str(x.mean()) + u", " + str(y.mean())
		print(string); f1w.write(string + u"\n")
	
		string = (u"\nMethods used are: \n" +
	    	      u"   - kmpfit:  kapteyn method, from " +
	        	  u"https://www.astro.rug.nl/software/kapteyn/kmpfittutorial.html \n" +
		          u"              with error on X and Y or Y only or none \n" +
		          u"   - ODR: Orthogonal Distance Regression \n" +
	    	      u"   - Williamson: least square fitting with errors in X and Y " +
	        	  u"according to \n" +
		          u"                 Williamson (Canadian Journal of Physics, 46, 1845-1847, 1968) \n")
		print(color.CYAN + string + color.END); f1w.write(string)
	
		beta0 = [5.0, 1.0]         # Initial estimates
		if struct[i_data][3] != 0 and struct[i_data][3] != None:
			if struct[i_data][1] != 0 or struct[i_data][1] != None:
				# Prepare fit routine
				fitobj = kmpfit.Fitter(residuals=residuals, data=(x, y, errx, erry))
				fitobj.fit(params0=beta0)
				string = (u"\n\n======== Results kmpfit: weights for both coordinates =========")
				print(color.BLUE + color.BOLD + string + color.END)
				f1w.write(string + "\n")
				string = (u"Fitted parameters:      " + str(fitobj.params) + u"\n"
				         u"Covariance errors:      " + str(fitobj.xerror) + u"\n"
				         u"Standard errors         " + str(fitobj.stderr) + u"\n"
				         u"Chi^2 min:              " + str(fitobj.chi2_min) + u"\n"
			    	     u"Reduced Chi^2:          " + str(fitobj.rchi2_min) + u"\n"
			        	 u"Iterations:             " + str(fitobj.niter))
				print(string); f1w.write(string + u"\n")
			else:
				# Prepare fit routine
				fitobj2 = kmpfit.Fitter(residuals=residuals2, data=(x, y, erry))
				fitobj2.fit(params0=beta0)
				string = (u"\n\n======== Results kmpfit errors in Y only =========")
				print(color.BLUE + color.BOLD + string + color.END)
				f1w.write(string + u"\n")
				string = (u"Fitted parameters:      " + str(fitobj2.params) + u"\n"
				          u"Covariance errors:      " + str(fitobj2.xerror) + u"\n"
				          u"Standard errors         " + str(fitobj2.stderr) + u"\n"
				          u"Chi^2 min:              " + str(fitobj2.chi2_min) + u"\n"
			    	      u"Reduced Chi^2:          " + str(fitobj2.rchi2_min))
				print(string); f1w.write(string)
	
		# Unweighted (unit weighting)
		fitobj3 = kmpfit.Fitter(residuals=residuals2, data=(x, y, np.ones(N)))
		fitobj3.fit(params0=beta0)
		string = (u"\n\n======== Results kmpfit unit weighting =========")
		print(color.BLUE + color.BOLD + string + color.END)
		f1w.write(string + "\n")
		string = (u"Fitted parameters:      " + str(fitobj3.params) + u"\n"
	    	      u"Covariance errors:      " + str(fitobj3.xerror) + u"\n"
	        	  u"Standard errors         " + str(fitobj3.stderr) + u"\n"
		          u"Chi^2 min:              " + str(fitobj3.chi2_min) + u"\n"
		          u"Reduced Chi^2:          " + str(fitobj3.rchi2_min))
		print(string); f1w.write(string)

		# Compare result with ODR
		# Create the linear model from statsfuncs
		linear = Model(model)
		if struct[i_data][3] != 0 and struct[i_data][3] != None:
			if struct[i_data][1] != 0 and struct[i_data][1] != None:
				mydata = RealData(x, y, sx=errx, sy=erry)
			else:
				mydata = RealData(x, y, sy=erry)
		else:
			mydata = RealData(x, y)
	
		myodr = ODR(mydata, linear, beta0=beta0, maxit=5000, sstol=1e-14)
		myoutput = myodr.run()
		string = (u"\n\n======== Results ODR =========")
		print(color.BLUE + color.BOLD + string + color.END)
		f1w.write(string + u"\n")
		string = (u"Fitted parameters:      " + str(myoutput.beta) + u"\n"
		          u"Covariance errors:      " + str(np.sqrt(myoutput.cov_beta.diagonal())) + u"\n"
	    	      u"Standard errors:        " + str(myoutput.sd_beta) + u"\n"
	        	  u"Minimum chi^2:          " + str(myoutput.sum_square) + u"\n"
		          u"Minimum (reduced)chi^2: " + str(myoutput.res_var))
		print(string); f1w.write(string)

		# Compute Williamson regression
		a_will, b_will, siga, sigb, beta, x_av, x__mean = williamson(x, y, errx, erry, struct[i_data], myoutput)
		
		if struct[i_data][3] != 0 and struct[i_data][3] != None:
			if struct[i_data][1] != 0 and struct[i_data][1] != None:
				chi2 = (residuals(fitobj.params,(x,y,errx,erry))**2).sum()
			else:
				chi2 = (residuals2(fitobj2.params,(x,y,erry))**2).sum()
		else:
			chi2 = (residuals2(fitobj3.params,(x,y,np.ones(N)))**2).sum()

		string = (u"\n\n======== Results Williamson =========")
		print(color.BLUE + color.BOLD + string + color.END)
		f1w.write(string + u"\n")
		string = (u"Average x weighted:     " + str(x_av) + u"\n"
		          u"Average x unweighted:   " + str(x__mean) + u"\n"
	    	      u"Fitted parameters:      " + u"[" + str(a_will) + u"," + str(b_will) + u"]\n"
	        	  u"Covariance errors:      " + u"[" + str(siga) + u"," + str(sigb) + u"]\n"
		          u"Minimum chi^2:          " + str(chi2))
		print(string); f1w.write(string)	
	
		string = (u"\n====================================="
		         u"\nPractical results:                     a       +       b     *   x")
		print(color.BLUE + color.BOLD + string + color.END)
		f1w.write(u"\n" + string + u"\n")
		string = (u"kmpfit unweighted:           %13.4f    %13.4f"
		         %(fitobj3.params[0], fitobj3.params[1]))
		print(string)
		f1w.write(string + u"\n")
		string = (u"   Exhumation Rate: %13.4f" %(1/fitobj3.params[1]))
		print(string)
		f1w.write(string + u"\n")
		string = (u"   Min. Exh. Rate: %13.4f" %(1/(fitobj3.params[1] - np.sqrt(fitobj3.stderr[1]))))
		print(string)
		f1w.write(string + u"\n")
		string = (u"   Max. Exh. Rate: %13.4f" %(1/(fitobj3.params[1] + np.sqrt(fitobj3.stderr[1]))))
		print(string)
		f1w.write(string + "\n")
		if struct[i_data][3] != 0 and struct[i_data][3] != None:
			if struct[i_data][1] != 0 and struct[i_data][1] != None:
				string = u"kmpfit effective variance:    %13.4f    %13.4f"%(fitobj.params[0], fitobj.params[1])
				print(string)
				f1w.write(string + u"\n")
				string = (u"   Exhumation Rate: %13.4f" %(1/fitobj.params[1]))
				print(string)
				f1w.write(string + u"\n")
				string = (u"   Min. Exh. Rate: %13.4f" %(1/(fitobj.params[1] - np.sqrt(fitobj.stderr[1]))))
				print(string)
				f1w.write(string + u"\n")
				string = (u"   Max. Exh. Rate: %13.4f" %(1/(fitobj.params[1] + np.sqrt(fitobj.stderr[1]))))
				print(string)
				f1w.write(string + u"\n")
			else:
				string = u"kmpfit weights in Y only:     %13.4f    %13.4f"%(fitobj2.params[0], fitobj2.params[1])
				print(string)
				f1w.write(string + u"\n")
				string = (u"   Exhumation Rate: %13.4f" %(1/fitobj2.params[1]))
				print(string)
				f1w.write(string + u"\n")
				string = (u"   Min. Exh. Rate: %13.4f" %(1/(fitobj2.params[1] - np.sqrt(fitobj2.stderr[1]))))
				print(string)
				f1w.write(string + u"\n")
				string = (u"   Max. Exh. Rate: %13.4f" %(1/(fitobj2.params[1] + np.sqrt(fitobj2.stderr[1]))))
				print(string)
				f1w.write(string + u"\n")
		string = u"ODR:                          %13.4f    %13.4f"%(beta[0], beta[1])
		print(string)
		f1w.write(string + u"\n")
		string = (u"   Exhumation Rate: %13.4f" %(1/beta[1]))
		print(string)
		f1w.write(string + u"\n")
		string = (u"   Min. Exh. Rate: %13.4f" %(1/(beta[1] - np.sqrt(myoutput.sd_beta[1]))))
		print(string)
		f1w.write(string + u"\n")
		string = (u"   Max. Exh. Rate: %13.4f" %(1/(beta[1] + np.sqrt(myoutput.sd_beta[1]))))
		print(string)
		f1w.write(string + u"\n")
		string = u"Williamson:                   %13.4f    %13.4f"%(a_will, b_will)
		print(string)
		f1w.write(string + u"\n")
		string = (u"   Exhumation Rate: %13.4f" %(1/b_will))
		print(string)
		f1w.write(string + u"\n")
		# For the next lines, not sure that we have to use the chi2 as error...
		string = (u"   Min. Exh. Rate: %13.4f" %(1/(b_will - chi2)))
		print(string)
		f1w.write(string + u"\n")
		string = (u"   Max. Exh. Rate: %13.4f" %(1/(b_will + chi2)))
		print(string)
		f1w.write(string + u"\n")
		print(u"\n")
	
		# calcul of confidence intervals
		dfdp = [1, x, x**2]
		if struct[i_data][3] != 0 and struct[i_data][3] != None:
			if struct[i_data][1] != 0 and struct[i_data][1] != None:
				ydummy, upperband, lowerband = confidence_band(x, dfdp, confprob, fitobj, model)
				labelconf = u"CI (" + str(confprob) + u"%) relative weighting in X & Y"
				if i_data == 0:
					#string = (u"y = a + b * x with a = %6.4f +/- %6.4f and b = %6.4f +/- %6.4f " 
					#stringl = (u"y_" + labeldata[i_data] + u" = a + b * x with a = %.2f +/- %.2f and b = %.2f +/- %.2f " 
					#stringl = (u" y_" + labeldata[i_data] + u" = a + b * x with a = %.2f +/- %.2f and b = %.2f +/- %.2f " 
					#           %(fitobj.params[0], np.sqrt(fitobj.stderr[0]), 
					#           fitobj.params[1], np.sqrt(fitobj.stderr[1])))
					stringl = (r" $\mathbf{Y_{%s}} = \mathbf{a} + \mathbf{b} \times \mathbf{X}$ with $\mathbf{a} = %.2f \pm %.2f$ and $\mathbf{b} = %.2f \pm %.2f$ " 
					           %(labeldata[i_data], fitobj.params[0], np.sqrt(fitobj.stderr[0]), 
					           fitobj.params[1], np.sqrt(fitobj.stderr[1])))
				else:
					#string = (u"y = a + b * x with a = %6.4f +/- %6.4f and b = %6.4f +/- %6.4f " 
					stringl = stringl + "\n" + (r"$\mathbf{Y_{%s}} = \mathbf{a} + \mathbf{b} \times \mathbf{X}$ with $\mathbf{a} = %.2f \pm %.2f$ and $\mathbf{b} = %.2f \pm %.2f$ " 
					                     %(labeldata[i_data], fitobj.params[0], np.sqrt(fitobj.stderr[0]), 
					                       fitobj.params[1], np.sqrt(fitobj.stderr[1])))
			else:
				ydummy, upperband, lowerband = confidence_band(x, dfdp, confprob, fitobj2, model)
				labelconf = u"CI (" + str(confprob) + u"%) relative weighting in Y"
				if i_data == 0:
					#string = (u"y = a + b * x with a = %6.4f +/- %6.4f and b = %6.4f +/- %6.4f " 
					stringl = (r"$\mathbf{Y_{%s}} = \mathbf{a} + \mathbf{b} \times \mathbf{X}$ with $\mathbf{a} = %.2f \pm %.2f$ and $\mathbf{b} = %.2f \pm %.2f$ " 
				    	     %(labeldata[i_data], fitobj2.params[0], np.sqrt(fitobj2.stderr[0]), 
				        	   fitobj2.params[1], np.sqrt(fitobj2.stderr[1])))
				
				else:
					#string = (u"y = a + b * x with a = %6.4f +/- %6.4f and b = %6.4f +/- %6.4f " 
					stringl = stringl + "\n" + (r"$\mathbf{Y_{%s}} = \mathbf{a} + \mathbf{b} \times \mathbf{X}$ with $\mathbf{a} = %.2f \pm %.2f$ and $\mathbf{b} = %.2f \pm %.2f$ " 
				    	                 %(labeldata[i_data], fitobj2.params[0], np.sqrt(fitobj2.stderr[0]), 
				        	               fitobj2.params[1], np.sqrt(fitobj2.stderr[1])))
		else:
			ydummy, upperband, lowerband = confidence_band(x, dfdp, confprob, fitobj3, model)
			labelconf = u"CI (" + str(confprob) + u"%) with no weighting"
			if i_data == 0:
				#string = (u"y = a + b * x with a = %6.4f +/- %6.4f and b = %6.4f +/- %6.4f " 
				stringl = (r"$\mathbf{y_{%s}} = \mathbf{a} + \mathbf{b} \times x$ with $\mathbf{a} = %.2f \pm %.2f$ and $\mathbf{b} = %.2f \pm %.2f$ " 
				         %(labeldata[i_data], fitobj3.params[0], np.sqrt(fitobj3.stderr[0]), 
				           fitobj3.params[1], np.sqrt(fitobj3.stderr[1])))
			else:
				#string = (u"y = a + b * x with a = %6.4f +/- %6.4f and b = %6.4f +/- %6.4f " 
				stringl = stringl + "\n" + (r"$\mathbf{Y_{%s}} = \mathbf{a} + \mathbf{b} \times \mathbf{X}$ with $\mathbf{a} = %.2f \pm %.2f$ and $\mathbf{b} = %.2f \pm %.2f$ " 
				                    %(labeldata[i_data], fitobj3.params[0], np.sqrt(fitobj3.stderr[0]), 
				                      fitobj3.params[1], np.sqrt(fitobj3.stderr[1])))
		#verts = zip(x, lowerband) + zip(x[::-1], upperband[::-1])
		# Because we need to invert X and Y for the graph
		verts = list(zip(lowerband, x)) + list(zip(upperband[::-1], x[::-1]))
		
		# Close output file
		f1w.close()


		#if rangex:
		#	X = np.linspace(rangex[0], rangex[1], 50)
		#else:
		#	d = (x.max() - x.min())/10
		#	X = np.linspace(x.min()-d, x.max()+d, 50)
		#if rangey: 
		#	Y = np.linspace(rangey[0], rangey[1], 50)
		#else:
		#	d = (y.max() - y.min())/10		
		#	Y = np.linspace(y.min()-d, y.max()+d, 50)
		# Call the plotting function
		#axes = plotgraphreg(struct[i_data], x, y, errx, erry, X, Y, 
		axes = plotgraphreg(struct[i_data], x, y, errx, erry, colors[i_data],
		                    labeldata[i_data], statstypes, a_will, b_will, 
		                    verts, confprob, fitobj, fitobj2, fitobj3)
	
	# Set graph characteristics/attributes
	plt.xlabel(labelx)
	plt.ylabel(labely)
	plt.grid(True)
	plt.title(stringl, size = fontsz)
	# clean the legend from duplicates
	handles, labels = plt.gca().get_legend_handles_labels()
	by_label = OrderedDict(zip(labels, handles))
	plt.legend(by_label.values(), by_label.keys(), loc="best")
	# set the X and Y limits
	if rangex: 
		axes.set_xlim([rangex[0], rangex[1]])
	if rangey: 
		axes.set_ylim(bottom = rangey[0], top = rangey[1])
		
	plt.savefig(work_dir[0] + output + u'.pdf')
	plt.close()

   
############################################################################
############################################################################

# Main code
if __name__ == u'__main__':
	
	# Run the code
	vertprofile()
	
# END of code
