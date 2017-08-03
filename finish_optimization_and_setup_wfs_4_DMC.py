#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
	import os
	import sys
	import lxml
	from glob import glob
	import numpy as np
	from lxml import etree

        ############################################################################
        ### get where the series should restart in case the calculation terminated early
        match = "Opt-*opt.xml"
        seriesNum = []
        for filename in glob(match):
                seriesNum.append(int(filename[-11:-8]))
        restartSeriesNum = str(max(seriesNum)+1)

	###################################################################################
        ## Grab the energy  and save it for future use (i.e. getting the lowest energy wavefunction)
	#os.system("OptProgress.pl *scalar.dat > opt_final.dat")
	os.system("qmca -q ev *scalar.dat > opt_final.dat")
	
	#################################################################################
	## Open the optimization file and get the project id (so we can copy the correct files) 
	## and grab the start of the series block
	optfile = "Opt.xml"
	tree= etree.parse(optfile)
	root = tree.getroot()
	initialSeries = float(root[0].get("series"))
        Optfileroot = root[0].get("id")
	

	###################################################################################
	## Get the energies and associated series number from the block we are looking at
	## use the file we just output the data into
	series=[]
	energies=[]
	prevEnergies=[]
	collectDat=False
        with open("opt_final.dat","r") as fileIn:
		for row in fileIn:
			if collectDat:
        			row = row.split("  ")
				serNum = int(row[1].split(" ")[1])
				if serNum >initialSeries:
					series.append("%03d" %serNum)
					energies.append(float(row[2].split(" ")[0]))
				else:	
					prevEnergies.append(float(row[2].split(" ")[0]))
	
			## this is a check in case the first row is empty
			elif "LocalEnergy" in row:
				collectDat=True
        
	
	####################################################################
	### get the index of the lowest energy
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

	run+=1


	############################################################################
	fileroot =sys.argv[1]
	myfile ="../"+fileroot+".wfs.xml"

	## Backup the wfs file
	os.system("cp "+myfile+" " +myfile+"_3b")
	############################################################################
	

	### Copy the wavefunction file with the lowest energy into the main wavefunction file
	os.system("cp "+Optfileroot +".s"+series[index]+".opt.xml "+myfile)
	### now open the main wavefunction file and add a comment tag stating what series was used
	if energies[index] <=Echeck:
		tree= etree.parse(myfile)
		root = tree.getroot()
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
	print "Check and submit DMC run"
	
