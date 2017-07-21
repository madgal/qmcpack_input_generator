#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import os
################################################
#### Generate : DMC.xml
################################################
import lxml
from lxml import etree

import sys

outerDir=sys.argv[1]
ptclfileroot=sys.argv[2]
wfsfileroot=sys.argv[3]
filename = sys.argv[4]
usepp = sys.argv[5]
elementList = sys.argv[6]
filePath = sys.argv[7]

if usepp:
    template_Name = "DMC_PP.xml"

    ## remove the bracket from the beginning and end then 
    ## parse by comma to get it back into list format
    elementList = elementList.replace("[","")
    elementList = elementList.replace("]","")
    elementList = elementList.split(",")

    for el in elementList:
		#os.system("cp /soft/applications/qmcpack/pseudopotentials/BFD/"+el + ".BFD.xml " + outerDir)
		os.system("cp ~/qmcpack-3.0.0/pseudopotentials/BFD/"+el + ".BFD.xml " + outerDir)

else:
    template_Name = "DMC_AE.xml"
    
DMC_dir = outerDir + "/DMC"
if not(os.path.isdir(DMC_dir)):
    os.mkdir(DMC_dir)
os.system("cp " + filePath + "misc/"+template_Name+" " +DMC_dir+"/DMC.xml")
os.system("cp " + filePath + "utils/format_data.py " +DMC_dir)


myFile = DMC_dir+"/DMC.xml"
tree = etree.parse(myFile)
root = tree.getroot()

project = root[0]
icld_ptcl = root[2]
icld_wfs = root[3]

if usepp:
	hamilt   = root[5] 
	pairPot1 = hamilt[0]

	count=0
	for el in elementList:
		pairPot1.append(etree.Element("pseudo"))
		pseudo = pairPot1[count]
		pseudo.set("elementType",el)
		el_path = os.path.abspath(outerDir+ "/"+el+".BFD.xml")

		pseudo.set("href",el_path)
		count+=1
	
projName = "DMC-"+filename
project.set("id",projName)

ptclFile = ptclfileroot+".ptcl.xml"
wfsFile =  wfsfileroot +".wfs.xml"
icld_ptcl.set("href",ptclFile)
icld_wfs.set("href",wfsFile)

###### NOW WRITE THE MODIFICATIONS TO A FILE
tmpfile = myFile+".tmp"
f = open( tmpfile,"w")
f.write("<?xml version=\"1.0\"?>\n")
f.write(etree.tostring(root,pretty_print=True))
f.close()

os.system("mv " + tmpfile + " " + myFile)

os.system("cp " +filePath + "misc/bgq-DMC.sh "+DMC_dir)
