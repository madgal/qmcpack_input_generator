#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
        ### import needed modules
	import os,sys
	from lxml import etree
	from glob import glob
	import numpy as np
	import argparse
	
        #####################################################################
	#### get the needed arguments from the command line
	parser = argparse.ArgumentParser(description='Optimize the wavefunction, keeping track of previous series')
	parser.add_argument('--optFile',help="The name of the optimization file")
	parser.add_argument('--wfsFile',help="The name of the wavefunction file")
	parser.add_argument('--optType',help="The type of optimization to try to begin (12,RC, 3B, or Fin)")
	parser.add_argument('--seriesNum',help="The number of the series used for continuing (1,2,...,999)")
	
        args = parser.parse_args()
	
	
        ### check that the optimization file exists
	if not(args.optFile):
		print "Error: An optimization file is needed"
		sys.exit(1)
	optFile = args.optFile
	if not(optFile.endswith(".xml")):
		if os.path.isfile(optFile +".xml"):
			optFile = optFile+".xml"
			print "Opt file is : %s" %optFile
		else:
			print "The optimization file (%s) does not exist" %optFile
			sys.exit(1)
		
	elif not(os.path.isfile(optFile)):
		print "The optimization file (%s) does not exist" %optFile
		sys.exit(1)
	else:
		print "Opt file is : %s" %optFile
		
	### check that the wavefunction file exists	
	if not(args.wfsFile):
		print "Error: A wavefunction file is needed"
		sys.exit(1)
	wfsFile = args.wfsFile
	if not(wfsFile.endswith(".xml")):
		if os.path.isfile(wfsFile +".xml"):
			wfsFile = wfsFile+".xml"
			print "Wavefunction file is : %s" %wfsFile
		else:
			print "The wavefunction file (%s) does not exist" %wfsFile
			sys.exit(1)
		
	elif not(os.path.isfile(wfsFile)):
		print "The wavefunction file (%s) does not exist" %wfsFile
		sys.exit(1)
	else:
		print "Wavefunction file is : %s" %wfsFile
	
        ### check that the user is trying to optimize with the correct options
	if not(args.optType):
		print "Error: The label for the next optimization step is needed"
		sys.exit(1)
	try_optType = args.optType
	if not(try_optType=="12" or try_optType=="RC" or try_optType=="3B" or try_optType=="Fin"):
		print "Please use:\n\t 12 for only optimizing 1 and 2 body\n\t RC for including coefficient reoptimization \n\t 3B for including 3 body Jastrow optimization"
		sys.exit(1)
	else:
		print  "Optimization type is %s" %try_optType
	

        ## check that user input series number
        if not(args.seriesNum):
                if try_optType=="12":
                        seriesNum=0
        		print "This is the first run so no series will be used"
	        else:
                        print "A series number is needed to continue optimization or start a DMC run"
                        sys.exit(1)
        else:
                seriesNum=args.seriesNum
                print "The series number for continuing is %s" %seriesNum    
        
        	
	##########################################################################
	##########################################################################
	##########################################################################
	#### Now begin the main program that the checks have been completed
	##########################################################################
	### Find which wavefunction files were produced
	### in case the calculation was killed 
	
        match = "*.opt.xml"
	seriesBlock=[]
	for filename in glob(match):
		seriesBlock.append(int(filename[-11:-8]))
	if len(seriesBlock)>0:
		restartSeriesNum = max(seriesBlock) +1
	else:
		restartSeriesNum=1
	
        ##########################################################################
	#### Open the optimization file to retrieve run information
	
        optTree = etree.parse(optFile)
	optRoot = optTree.getroot()
	### pull the start of the series group
	initialSeries = int(optRoot[0].get("series"))
	### get the name of the optimization files
	Optfileroot  = optRoot[0].get("id") +".s"
	
        ## now modify the file
	optRoot[0].set("series",str(restartSeriesNum))
	optTmpFile=optFile+".tmp"
	fOpt = open(optTmpFile,"w")
	fOpt.write("<?xml version=\"1.0\"?>\n")
	fOpt.write(etree.tostring(optRoot,pretty_print=True))
	fOpt.close()
	## the original will be overwritten only if there are no errors
	
        #########################################################################
	##### Grab information about the previous run 
	
	##### if it is the first run then create the information 
	if not(os.path.isfile("opt_run_info.dat")):
		### and create the file
		with open("opt_run_info.dat","w") as fileOut:
			fileOut.write("optType,run,seriesNumUsed,seriesStart\n")
			## optType tells which optimization is occuring
			## run is for backup files
			## seriesNumUsed is for user info
			## seriesStart is for user info
			### set the values for the first run
			run=0 # initialize the run value
			seriesNum=0	 # set the seriesNum as zero
	
        else: # the file exists so grab the information
		with open("opt_run_info.dat","r") as fileIn:
			# get the last line in the file which corresponds to the last run
			lastrun = fileIn.read().splitlines()[-1] 
		lastrun = lastrun.split(",")
		### multiple runs have occurred
		#prev_optType=lastrun[0]
		run = int(lastrun[1])	
		# seriesNumUsed =int(lastrun[2])	
		#seriesStart = int(lastrun[3]) # this is mainly for users in case they want to redo previous steps
	
        ########################################################################
	### backup the wavefunction file
        os.system("cp " + wfsFile + " " + wfsFile +"_"+str(run))
        
        print seriesNum
        newWavefunction ="%s%03d.opt.xml" %(Optfileroot,int(seriesNum))
        if os.path.isfile(newWavefunction):
                os.system("cp " + newWavefunction + " " + wfsFile)
        elif seriesNum>1:
                print "Error: %s does not exist" %newWavefunction
                sys.exit(1)
	else:
		print "The original wavefunction has been backed up"
	
	run+=1## update the run value to be on the run getting setup
	###########################################################################
	#### open the wavefunction and get info depending on type of optimization
	
	wfsTree = etree.parse(wfsFile)
	wfsRoot = wfsTree.getroot()
	wavefunc = wfsRoot[0]
	optType=""
	
	## check for 1 and 2 body 
	try:
		j2Body= wavefunc[1]
		j1Body= wavefunc[2]
		if j2Body.tag=="jastrow" and  j1Body.tag=="jastrow":
        		optType="12"
	except Exception as e:
		print "No 1 and 2 body Jastrow"
	
	try: 
		detset=wavefunc[0]
		multidet=detset[3]
		mdO = multidet.get("optimize")[0].lower()=="y"
		if mdO:
			optType = optType +"_RC"
	except Exception as e:
		print "Single determinant system"
			
	try:
		j3Body = wavefunc[3]
		j3O = j3Body[0][0].get("optimize")[0].lower()=="y"
		if j3O:
        		optType=optType + "_3B"
	except Exception as e:
        	print "No 3 body Jastrow "
	
	#######################################################################
	#### setup the wavefunction for the next round of optimization #######
	
	### go to next step in optimization
	### modify the wavefunction
	if try_optType=="12":
		### make sure the rcut values are correct
		for corr in j2Body:
	            corr.set("rcut","10")
		for corr in j1Body:
	            corr.set("rcut","5")
		try:
			## if using a 3 body Jastrow, set rcut to 3 and make sure to not optimize
			for corr in j3Body:
	    			corr.set("rcut","3")
	    			corr[0].set("optimize","no")
		except Exception:
			print "No 3 body Jastrow"
		try:
			## if there is a multideterminant make sure to not optimize
        		multidet.set("optimize","no")
		except Exception:
			print "Single determinant system"
	
		print "System is ready for ",try_optType," optimization"
	elif try_optType =="RC":
		multidet.set("optimize","yes")
    		print "System is ready for ",try_optType," optimization"
	elif try_optType=="3B":
		for corr in j3Body:
			corr.set("rcut","3")
			corr[0].set("optimize","yes")
		print "System is ready for ",try_optType," optimization"
        elif try_optType=="Fin":
		print "System is ready for DMC"
        	
	
	### modify the wfsfile each time to (at the very least) include which series it is
	
	if seriesNum>1:
		wfsTmpfile = wfsFile + ".tmp"
		fWfs = open(wfsTmpfile,"w")
		fWfs.write("<?xml version=\"1.0\"?>\n")
		fWfs.write("<!-- s%s -->\n" %seriesNum)
		fWfs.write(etree.tostring(wfsRoot,pretty_print=True))
		fWfs.close()
		### if there are no errors then we will overwrite the file
	else:
		wfsTmpfile = wfsFile + ".tmp"
		fWfs = open(wfsTmpfile,"w")
        	fWfs.write("<?xml version=\"1.0\"?>\n")
		fWfs.write(etree.tostring(wfsRoot,pretty_print=True))
		fWfs.close()
	
	### output the run information to the file
	with open("opt_run_info.dat","a") as fileOut:
		fileOut.write("%s,"%try_optType)
	fileOut.write("%s,"%run)
	fileOut.write("%s,"%seriesNum)
	fileOut.write("%s\n"%restartSeriesNum)
except Exception:
	print "There was an error. Check the arguments and files"

else:
	### there were no errors or failures ##############################

	### overwrite the optimization file with the modifications 
	os.system("mv " + optTmpFile + "  " + optFile)

	###  overwrite the wavefunctino file with the modifications

	os.system("mv " + wfsTmpfile + " " + wfsFile)
			
	print "finished"
