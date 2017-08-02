#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

try:
        import lxml
        from lxml import etree
        from glob import glob
        fileroot = sys.argv[1] 

        myfile ="../"+fileroot+".wfs.xml"
	## Backup the wfs file
	os.system("cp "+ myfile +" " +myfile + "_12Opt")

	###################################################################################
        ## Grab the energy  and save it for future use (i.e. getting the lowest energy wavefunction)
	#os.system("OptProgress.pl *scalar.dat > opt_1b2b.dat")
	os.system("qmca -q ev *scalar.dat > opt_1b2b.dat")

	###################################################################################
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
				series.append("%03d" %serNum)
				energies.append(float(row[2].split(" ")[0]))
			#check to see if we are to the data yet
			elif "LocalEnergy" in row:
				collectDat=True

	## get the index of the lowest energy wavefunction
	index = energies.index(min(energies))
	print  "Series %s will be used" %series[index]

	###################################################################################
	## copy the lowest energy wavefunction to the main wavefunction file
	Optfileroot = row[0]+".s"
	os.system("cp " + Optfileroot+series[index]+".opt.xml "+myfile)

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

	###################################################################################
	### get where the series should restart
	match = "Opt-*opt.xml"
	seriesNum = []
        for filename in glob(match):
                seriesNum.append(int(filename[-11:-8]))
        restartSeriesNum = str(max(seriesNum)+1)

	### update where the series will start
	myfile = "Opt.xml"
   	tree= etree.parse(myfile)
	root = tree.getroot()
	root[0].set("series",restartSeriesNum)

	tmpfile = myfile+".tmp"
	f = open( tmpfile,"w")
	f.write("<?xml version=\"1.0\"?>\n")
	f.write(etree.tostring(root,pretty_print=True))
	f.close()

	os.system("mv " + tmpfile + " " + myfile)

 
except Exception:
	print "Please check filenames and existence of files" 
else:
	print "Check and submit Optimization including coefficient reoptimization"
 
