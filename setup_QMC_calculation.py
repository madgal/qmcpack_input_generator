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
    sys.path.insert(0, thispath+"src/")

    import setupMethods 
    from docopt import docopt
    version="0.0.1"
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
		necessaryInfo = setupMethods.useQuantumPackageMethod(filename)

	#elif method=="":
		#necessaryInfo = setupMethods.useOtherMethod(filename)

	[elementList,numDet,convertType,doPseudo,multidet,fileroot] = necessaryInfo

	'''
	Now we begin the conversion and building of the necessary directories
	'''
	dirName =""
	flags=""
	if nojastrow:
		dirName=dirName+"NoJastrow_"
		flags = flags+ "-nojastrow "
	elif use3Body:
		dirName=dirName+"Jastrow123_"
		flags = flags+"-add3BodyJ "
	else:
		dirName=dirName+"Jastrow12_"

	if not(doPseudo):
		flags = flags +"-addCusp "

	if multidet:
		dirName = dirName +"MultiDet"
	else:
		dirName = dirName +"1Det"
	if reopt:
		dirName = dirName + "_reopt"


	if not(os.path.isdir(dirName)):
		os.mkdir(dirName)
	local_fileroot = dirName +"/"+fileroot
	print "The input files will be place in ",dirName

	#os.system("./misc/converter_independent.py "+convertType+" "+ filename+" "+ local_fileroot+" "+ flags)
	import converter_independent
	print "Beginning conversion"
	converter_independent.do_conversion(convertType,filename,local_fileroot,flags)
	print "Finished Conversion"

	absfileroot = os.getcwd() + "/"+dirName + "/"+ fileroot


	for trypath in sys.path:
		if os.path.exists(trypath+"generateCutoffDirs4QMC.py"):
			filePath = trypath
			break

	### the files should be in one of these two paths which we appended 
	### so that we could find the files when we executed them outside the
	### directory containing them 
	trypath1 = sys.path[0]
	trypath2 = sys.path[1]
	if multidet:
		print "Multi reference system"
		### this will call another program which will generate
		### cutoff directories containing 
		### optimization and DMC folders
		import generateCutoffDirs4QMC
		generateCutoffDirs4QMC.generateCutoff(dirName,absfileroot,fileroot,doPseudo,elementList,filePath)
		
	else:
		print "Single reference system"
		### generate the DMC and Optimization folders
		import setupDMCFolder
		setupDMCFolder.makeFolder(dirName,absfileroot,absfileroot,fileroot,doPseudo,elementList,filePath)
		import setupOptFolder
		setupOptFolder.makeFolder(dirName,absfileroot,absfileroot,fileroot,doPseudo,elementList,filePath)
	if not(doPseudo):
		#os.system("./misc/setupCuspCorrection.py "+dirName+ " " + absfileroot+" " +multidet)
		print "This is an all electron calculation so the Cusp correction is being added"
		import setupCuspCorrection 
		setupCuspCorrection.generate_CuspDir(dirName,absfileroot,multidet,filePath)
		
