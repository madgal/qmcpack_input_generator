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


	##########################################################################
	##########################################################################
	##########################################################################
	#### Now begin the main program that the checks have been completed
	##########################################################################
	### Find which wavefunction files were produced
	### in case the calculation was killed 

	match = "*.opt.xml"
	seriesNum=[]
	for filename in glob(match):
		seriesNum.append(int(filename[-11:-8]))
	if len(seriesNum)>0:
		restartSeriesNum = max(seriesNum) +1
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

	##########################################################################
	### Grab the energies and save it for future use
	### (i.e. getting the lowest energy wavefunction)

	if restartSeriesNum>1:
		energyFilename = "opt_energy_qmca.dat"
		os.system("qmca -q ev *scalar.dat > "+energyFilename )


		##########################################################################
		#### Get the energies for the group we are interested in 
		#### but don't look at the VMC energy or other series we don't have a 
		#### wavefunction for.
		
		series=[]
		energies=[]
		collectDat=False
		with open(energyFilename,"r") as fileIn:
			for row in fileIn:	
				if collectDat:
					row = row.split("  ")
	                                serNum = int(row[1].split(" ")[1])
        	                        if serNum >initialSeries+1 and serNum < restartSeriesNum:
                	                        series.append("%03d" %serNum)
                        	                energies.append(float(row[2].split(" ")[0]))
                        	#check to see if we are to the data yet
                        	elif "LocalEnergy" in row:
                        	        collectDat=True

	#########################################################################
	##### Grab information about the previous run 
	
	##### if it is the first run then create the information 
	if not(os.path.isfile("opt_run_info.dat")):
		### and create the file
		with open("opt_run_info.dat","w") as fileOut:
			fileOut.write("optType,run,Echeck,seriesStart\n")

	
	else: # the file exists so grab the information
		with open("opt_run_info.dat","r") as fileIn:
			# get the last line in the file which corresponds to the last run
			lastrun = fileIn.read().splitlines()[-1] 
		lastrun = lastrun.split(",")
		if lastrun[0]=="optType":
			### only one run has been done so far
			prev_optType="12" ### the first runs should optimize the 1 and 2 body Jastrows
			run=0 ## no previous run
			Echeck = np.mean(energies) 
			seriesStart=1
			
		else:
			### multiple runs have occurred
			prev_optType=lastrun[0]
			run = int(lastrun[1])	
			Echeck = float(lastrun[2])
			#seriesStart = int(lastrun[3]) # this is mainly for users in case they want to redo previous steps


	###########################################################################
	### get the index of  the lowest energy wavefunction
	if restartSeriesNum >1:
		index = energies.index(min(energies))
		### overwrite the wavefunction with the new one
		### but first back it up
		os.system("cp " + wfsFile + " " + wfsFile +"_"+str(run))
		print "Series %s will be used " %series[index] 
		os.system("cp " + Optfileroot + series[index]+".opt.xml " + wfsFile)
	else:
		###  first back it up
		os.system("cp " + wfsFile + " " + wfsFile +"_BAK")

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
		print "No coefficient reoptimization"
			
	try:
		j3Body = wavefunc[3]
		j3O = j3Body[0][0].get("optimize")[0].lower()=="y"
		if j3O:
			optType=optType + "_3B"
	except Exception as e:
		print "No 3 body Jastrow optimization"

	#######################################################################
	#### check that the system is being correctly optimized ##############
	
	modifyWfsForNextStep = (restartSeriesNum==1) or (energies[index] <= Echeck) 

	if modifyWfsForNextStep:
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
			
	else:
		print "Please check the energies and wavefunctions before submitting another optimization run"
		

	### modify the wfsfile each time to (at the very least) include which series it is

	if restartSeriesNum >1:
		wfsTmpfile = wfsFile + ".tmp"
		fWfs = open(wfsTmpfile,"w")
		fWfs.write("<?xml version=\"1.0\"?>\n")
		fWfs.write("<!-- s%s -->\n" %series[index])
		fWfs.write(etree.tostring(wfsRoot,pretty_print=True))
		fWfs.close()
		### if there are no errors then we will overwrite the file


		if prev_optType==optType:
			run +=1
		else:
			run=1

		### output the run information to the file
		with open("opt_run_info.dat","a") as fileOut:
			fileOut.write("%s,"%optType)
			fileOut.write("%s,"%run)
			fileOut.write("%s,"%np.mean(energies))
			fileOut.write("%s\n"%initialSeries)
	else:
		wfsTmpfile = wfsFile + ".tmp"
		fWfs = open(wfsTmpfile,"w")
		fWfs.write("<?xml version=\"1.0\"?>\n")
		fWfs.write(etree.tostring(wfsRoot,pretty_print=True))
		fWfs.close()

except Exception:
	print "There was an error. Check the arguments and files"

else:
	### there were no errors or failures ##############################

	### overwrite the optimization file with the modifications 
	os.system("mv " + optTmpFile + "  " + optFile)

	###  overwrite the wavefunctino file with the modifications

	os.system("mv " + wfsTmpfile + " " + wfsFile)
			
	print "finished"
