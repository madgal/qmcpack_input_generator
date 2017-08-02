#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import numpy as np

try:
	import lxml
	from lxml import etree
	from glob import glob
	fileroot = sys.argv[1]
        myfile ="../"+fileroot +".wfs.xml"
	## Backup the wfs file
	os.system("cp "+ myfile +" " +myfile + "_no3Body")

	###################################################################################
        ## Grab the energy  and save it for future use (i.e. getting the lowest energy wavefunction)
	#os.system("OptProgress.pl *scalar.dat > opt_without3Body.dat")
	os.system("qmca -q ev *scalar.dat > opt_without3Body.dat")

	### Get which wavefunctions have an *opt.xml file in case the calculation was killed
	match = "Opt-*.opt.xml"
	seriesNum = []
	for filename in glob(match):
		seriesNum.append(int(filename[-11:-8]))
 	maxSeriesNum = max(seriesNum)

	#################################################################################
	## Open the optimization file and get the project id (so we can copy the correct files) 
	## and grab the start of the series block
	optfile = "Opt.xml"
   	tree= etree.parse(optfile)
	root = tree.getroot()
	## pull the first series number we want to check with 
	initialSeries = int(root[0].get("series"))
	root[0].set("series",str(maxSeriesNum+1))
        Optfileroot = root[0].get("id")

	tmpfile = optfile+".tmp"
	f = open( tmpfile,"w")
	f.write("<?xml version=\"1.0\"?>\n")
	f.write(etree.tostring(root,pretty_print=True))
	f.close()

	os.system("mv " + tmpfile + " " + optfile)

	###################################################################################
	## Get the energies and associated series number from the block we are looking at
	## use the file we just output the data into
	series=[]
	energies=[]
	prevEnergies=[]
	collectDat=False
	with open("opt_without3Body.dat","r") as fileIn:
		for row in fileIn:
			if collectDat:
				row = row.split("  ")
				serNum = int(row[1].split(" ")[1])
				if serNum >initialSeries+1:
					series.append("%03d" %serNum)
				
					energies.append(float(row[2].split(" ")[0]))
				else:	
					prevEnergies.append(float(row[2].split(" ")[0]))

			#check to see if we are to the data yet
			elif "LocalEnergy" in row:
				collectDat=True

	###################################################################################
	## check to see if we are converging before we add in the Jastrows
	## but if the initial series was 1 there is no previous series block to check for
	if(initialSeries==1 or (np.mean(energies) < np.mean(prevEnergies))):
		### If you get here then 
		###    1) Only the 1 and 2 body have been optimized so far
		###    2) the coefficients are probably optimized or going in the correct direction

		## get the index of the lowest energy wavefunction
		index = energies.index(min(energies))
		print  "Series %s will be used" %series[index]
	
		## copy the lowest energy wavefunction to the main wavefunction file
		os.system("cp " + Optfileroot+series[index]+".opt.xml "+myfile)

		## change the main wavefunction file to include 3body Jastrow optimization
		## and add a comment tag to track which series was used
		tree= etree.parse(myfile)
		root = tree.getroot()
		wavefunc = root[0]
		determinantset = wavefunc[0]
		j3Body = wavefunc[3]

		for corr in j3Body:
			corr[0].set("optimize","yes")

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
	print "Check and submit Optimization with inclusion of 3 body Jastrow"
