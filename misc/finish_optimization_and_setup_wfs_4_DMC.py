#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import lxml
from lxml import etree

fileroot =sys.argv[1]
myfile ="../"+fileroot+".wfs.xml"

os.system("cp "+myfile+" " +myfile+"_3b")


os.system("OptProgress.pl *scalar.dat > opt_3b.dat")

optfile = "Opt.xml"
tree= etree.parse(optfile)
root = tree.getroot()
## pull the first series number we want to check with 
initialSeries = float(root[0].get("series"))

series=[]
energies=[]
prevEnergies=[]
with open("opt_3b.dat","r") as fileIn:
	for row in fileIn:
		row = row.split("  ")
		if int(row[0]) >initialSeries:
			series.append(row[0])
			energies.append(float(row[1]))
		else:	
			prevEnergies.append(float(row[1]))
	

index = energies.index(min(energies))
print series[index]
os.system("cp Opt-"+fileroot +".s"+series[index]+".opt.xml "+myfile)
