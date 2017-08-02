#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
	import os
	import sys
	import lxml
	from lxml import etree

	fileroot =sys.argv[1]
	myfile ="../"+fileroot+".wfs.xml"

	## Backup the wfs file
	os.system("cp "+myfile+" " +myfile+"_3b")
	
	#################################################################################
	## Open the optimization file and get the project id (so we can copy the correct files) 
	## and grab the start of the series block
	optfile = "Opt.xml"
	tree= etree.parse(optfile)
	root = tree.getroot()
	initialSeries = float(root[0].get("series"))
        Optfileroot = root[0].get("id")
	
	###################################################################################
        ## Grab the energy  and save it for future use (i.e. getting the lowest energy wavefunction)
	#os.system("OptProgress.pl *scalar.dat > opt_final.dat")
	os.system("qmca -q ev *scalar.dat > opt_final.dat")
	
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
        
	
	### get the index of the lowest energy
        index = energies.index(min(energies))
	print  "Series %s will be used" %series[index]
	### Copy the wavefunction file with the lowest energy into the main wavefunction file
	os.system("cp "+Optfileroot +".s"+series[index]+".opt.xml "+myfile)
	### now open the main wavefunction file and add a comment tag stating what series was used
	tree= etree.parse(myfile)
	root = tree.getroot()
	tmpfile = myfile+".tmp"
	f = open( tmpfile,"w")
	f.write("<?xml version=\"1.0\"?>\n")
	f.write("<!-- s%s -->\n" %series[index])
        f.write(etree.tostring(root,pretty_print=True))
	f.close()
	
        os.system("mv " + tmpfile + " " + myfile)
except Exception:
	print "Please check filenames and existence of files" 
else:
	print "Check and submit DMC run"
	
