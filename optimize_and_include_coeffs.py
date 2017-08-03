#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

try:
        import lxml
        from lxml import etree
        from glob import glob
	import numpy as np

	### First get the optimizaition information
	############################################################################
	### get where the series should restart in case the calculation terminated early
	match = "Opt-*opt.xml"
	seriesNum = []
        for filename in glob(match):
                seriesNum.append(int(filename[-11:-8]))
        restartSeriesNum = str(max(seriesNum)+1)

	############################################################################
        ## Grab the energy  and save it for future use (i.e. getting the lowest energy wavefunction)
	os.system("qmca -q ev *scalar.dat > opt_1b2b.dat")

	## Get the energies and associated series number from the block we are looking at
	## use the file we just output the data into
	series=[]
	energies=[]
	collectDat=False
	with open("opt_1b2b.dat","r") as fileIn:
		for row in fileIn:
			if collectDat:
				row = row.split("  ")
				serNum = int(row[1].split(" ")[1])
				if serNum < restartSeriesNum:
					series.append("%03d" %serNum)
					energies.append(float(row[2].split(" ")[0]))
			#check to see if we are to the data yet
			elif "LocalEnergy" in row:
				collectDat=True


	############################################################################
	### From the optimization file get what series we started at
	### and update where the series will restart
	optfile = "Opt.xml"
   	tree= etree.parse(optfile)
	root = tree.getroot()
	initSeries=root[0].get("series")
	root[0].set("series",restartSeriesNum)

	tmpfile = optfile+".tmp"
	f = open( tmpfile,"w")
	f.write("<?xml version=\"1.0\"?>\n")
	f.write(etree.tostring(root,pretty_print=True))
	f.close()

	os.system("mv " + tmpfile + " " + optfile)


	############################################################################
	## get the index of the lowest energy wavefunction
	index = energies.index(min(energies))
	print  "Series %s will be used" %series[index]

	### either create the optimization information file
	### update the optimization information file for the run just completed
	if not(os.path.isfile("opt_run_info.dat")):
		## then the data is coming from 1 and 2 body optimization
		optType = "12" #the previous run was for 1 and 2 body jastrow
		run = 0
		Echeck = np.mean(energies) #energies[index]
		seriesStart = 1
		with open("opt_run_info.dat","w") as fileOut:
			fileOut.write("optType,run,Echeck,seriesStart\n")
			#fileOut.write("%s,%s,%s,%s\n" %(optType,run,Echeck,seriesStart))

	### or grab the last line from the file
	else:	
		with open("opt_run_info.dat","r") as fileOut:
			### grab information about the previous optimization run
			myData = fileOut.read().splitlines()[-1]
		myData = myData.split(",")
		optType = myData[0]
		run = int(myData[1])
		Echeck = float(myData[2])
		seriesStart = int(myData[3])

	#################################################################################
        fileroot = sys.argv[1] 
        myfile ="../"+fileroot+".wfs.xml"
	## Backup the wfs file in case you want to return to a previous version
	os.system("cp "+ myfile +" " +myfile + "_12Opt_run"+str(run))
	## pull info from the wavefunction file

	tree= etree.parse(myfile)
	root = tree.getroot()
	wavefunc = root[0]
	determinantset = wavefunc[0]
	multidet = determinantset[3]
	mdO = multidet.get("optimize")[0].lower()=="y"
	if mdO and optType!="RC":
		optType="RC"
		run=1
		runModification=True
	else:
		run +=1
		runModification=False

	############################################################################
	## copy the lowest energy wavefunction to the main wavefunction file
	Optfileroot = row[0]+".s"
	os.system("cp " + Optfileroot+series[index]+".opt.xml "+myfile)

	#################################################################################
	#### check if we should move onto 1 Body, 2 Body, and coefficient reoptimization
	if  energies[index] <= Echeck and runModification:
		## include re-optimization of coefficients
		## if optType=="RC": then the coefficients are already being optimized

		## change the main wavefunction file to include multideterminant optimization
		## and add a comment tag to track which series was used
		tree= etree.parse(myfile)
		root = tree.getroot()
		wavefunc = root[0]
		determinantset = wavefunc[0]
		multidet = determinantset[3]
		multidet.set("optimize","yes")

		tmpfile = myfile+".tmp"
		f = open( tmpfile,"w")
		f.write("<?xml version=\"1.0\"?>\n")
		f.write("<!-- s%s -->\n" %series[index])
		f.write(etree.tostring(root,pretty_print=True))
		f.close()

		os.system("mv " + tmpfile + " " + myfile)
 
	## output the information for this run
	with open("opt_run_info.dat","a") as fileOut:
		fileOut.write("%s,%s,%s,%s\n" %(optType,run,np.mean(energies),initSeries))

except Exception:
	print "Please check filenames and existence of files" 
else:
	print "Check and submit Optimization including coefficient reoptimization"
 
