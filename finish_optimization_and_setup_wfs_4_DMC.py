#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import lxml
from lxml import etree

fileroot =sys.argv[1]
myfile ="../"+fileroot+".wfs.xml"

os.system("cp "+myfile+" " +myfile+"_3b")


#os.system("OptProgress.pl *scalar.dat > opt_3b.dat")
os.system("qmca -q ev *scalar.dat > opt_3b.dat")

optfile = "Opt.xml"
tree= etree.parse(optfile)
root = tree.getroot()
## pull the first series number we want to check with 
initialSeries = float(root[0].get("series"))
Optfileroot = root[0].get("id")

series=[]
energies=[]
prevEnergies=[]
collectDat=False
with open("opt_3b.dat","r") as fileIn:
	for row in fileIn:
		if collectDat:
			row = row.split("  ")
			serNum = int(row[1].split(" ")[1])
			if serNum >initialSeries:
				series.append("%03d" %serNum)
				energies.append(float(row[2].split(" ")[0]))
			else:	
				prevEnergies.append(float(row[2].split(" ")[0]))

		elif "LocalEnergy" in row:
			collectDat=True


index = energies.index(min(energies))
print series[index]
os.system("cp "+Optfileroot +".s"+series[index]+".opt.xml "+myfile)
tree= etree.parse(myfile)
root = tree.getroot()
tmpfile = myfile+".tmp"
f = open( tmpfile,"w")
f.write("<?xml version=\"1.0\"?>\n")
f.write("<!-- s%03d -->\n" %series[index])
f.write(etree.tostring(root,pretty_print=True))
f.close()

os.system("mv " + tmpfile + " " + myfile)
	

