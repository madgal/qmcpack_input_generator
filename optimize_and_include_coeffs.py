#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

try:
        import lxml
        from lxml import etree
        from glob import glob
        fileroot = sys.argv[1] 

	print "The wavefunction used is \"../%s.wfs.xml\"\n" %fileroot

        myfile ="../"+fileroot+".wfs.xml"
	os.system("cp "+ myfile +" " +myfile + "_12Opt")

	#os.system("OptProgress.pl *scalar.dat > opt_1b2b.dat")
	os.system("qmca -q ev *scalar.dat > opt_1b2b.dat")


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
			elif "LocalEnergy" in row:
				collectDat=True

	
	index = energies.index(min(energies))
	print series[index]

	Optfileroot = row[0]+".s"
	os.system("cp " + Optfileroot+series[index]+".opt.xml "+myfile)

	tree= etree.parse(myfile)
	root = tree.getroot()
	wavefunc = root[0]
	determinantset = wavefunc[0]
	multidet = determinantset[3]
	multidet.set("optimize","yes")

	tmpfile = myfile+".tmp"
	f = open( tmpfile,"w")
	f.write("<?xml version=\"1.0\"?>\n")
	f.write(etree.tostring(root,pretty_print=True))
	f.close()

	os.system("mv " + tmpfile + " " + myfile)

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
	print "Check and submit Optimization of coefficients with 1 and 2 body Jastrows"
 
