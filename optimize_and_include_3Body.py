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
	os.system("cp "+ myfile +" " +myfile + "_no3Body")

	os.system("OptProgress.pl *scalar.dat > opt_without3Body.dat")

	match = "Opt-"+fileroot + "*.opt.xml"
	seriesNum = []
	for filename in glob(match):
		seriesNum.append(int(filename[-11:-8]))
 	maxSeriesNum = max(seriesNum)

   	### update where the series will start
	optfile = "Opt.xml"
   	tree= etree.parse(optfile)
	root = tree.getroot()
	## pull the first series number we want to check with 
	initialSeries = int(root[0].get("series"))
	root[0].set("series",str(maxSeriesNum+1))

	tmpfile = optfile+".tmp"
	f = open( tmpfile,"w")
	f.write("<?xml version=\"1.0\"?>\n")
	f.write(etree.tostring(root,pretty_print=True))
	f.close()

	os.system("mv " + tmpfile + " " + optfile)

        ########################################

	series=[]
	energies=[]
	prevEnergies=[]
	with open("opt_without3Body.dat","r") as fileIn:
		for row in fileIn:
			row = row.split("  ")
			if int(row[0]) >initialSeries+1:
				series.append(row[0])
				energies.append(float(row[1]))
			else:	
				prevEnergies.append(float(row[1]))
		

	if( np.mean(energies) < np.mean(prevEnergies)):
	
		### Then the coefficients are probably optimized
		index = energies.index(min(energies))
		print series[index]
	
		os.system("cp Opt-" + fileroot+".s"+series[index]+".opt.xml "+myfile)

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
		f.write(etree.tostring(root,pretty_print=True))
		f.close()

		os.system("mv " + tmpfile + " " + myfile)
	
	#else:
	#resubmit the optimization without changing initial file
	

 
except Exception:
	print "Please check filenames and existence of files" 
else:
	print "Check and submit Optimization of coefficients with 1 and 2 body Jastrows"
