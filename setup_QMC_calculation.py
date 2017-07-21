#!/usr/bin/env python
# -*- coding: utf-8 -*-


## This code generates input to QMCPack by using quantum_package code

""" 
Usage: 
  setup_QMC_calculation.py (-h | --help)
  setup_QMC_calculation.py setup --filename=<filename.ext>
			--method=<QP>
			[--noJastrow=<True,False>]
			[--3BodyJ=<True,False>]
			[--reoptimizeCoeffs=<True,False>]

Example of use:
	./setup_QMC_calculation.py setup  --filename=qp_dumpfilename --method=QP --reoptimizeCoeffs=True
"""

### defaults to adding 3BodyJ

try:
    import os
    import sys
    thispath = os.path.abspath(sys.argv[0])
    thispath = thispath.replace("setup_QMC_calculation.py","")
    #print (thispath)
    #print os.path.isdir(thispath)
    #print thispath
    sys.path.insert(0, thispath)
    sys.path.insert(0, thispath+"misc/")

    import setupMethods 
    version="0.0.1"
    from src.docopt import docopt
except:
    print "File is corupted. Git reset may fix the issues"
    sys.exit(1)

if __name__ == '__main__':

    arguments = docopt(__doc__, version='G2 Api ' + version)


    ### Retrieve the arguments passed by the user
    if not (arguments["--filename"] and arguments["--method"]):
	print "The filename and conversionType are required"
	sys.exit(1)
    else:
	filename= arguments["--filename"]
	method  = arguments["--method"]

	if arguments["--noJastrow"]:
		nojastrow = arguments["--noJastrow"]=="True"
	else:
		nojastrow = False

	if arguments["--3BodyJ"]:
		use3Body = arguments["--3BodyJ"]=="True"
	else:
		use3Body = True
	if arguments["--reoptimizeCoeffs"]:
		reopt = arguments["--reoptimizeCoeffs"]=="True"
	else:
		reopt=False

	if method=="QP":
		setupMethods.useQuantumPackageMethod(filename,nojastrow,use3Body,reopt)

	print "Everything is done"
