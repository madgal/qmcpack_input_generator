#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os 
import lxml
from lxml import etree
import sys

fileroot = sys.argv[1]
myfile ="../"+fileroot+".wfs.xml"
os.system("cp "+myfile+" " + myfile+"_initial")

tree= etree.parse(myfile)
root = tree.getroot()
wavefunc = root[0]
determinantset = wavefunc[0]

up_det =  determinantset[1][0]
dn_det = determinantset[1][1]

fulldir=os.getcwd()
MyCuspUp =fulldir+"/updet.cuspInfo.xml"
up_det.set("cuspInfo",MyCuspUp)
MyCuspDn =fulldir+"/downdet.cuspInfo.xml"
dn_det.set("cuspInfo",MyCuspDn)


try:
	j2Body= wavefunc[1]
	j1Body= wavefunc[2]
	for corr in j2Body:
	    corr.set("rcut","10")
	for corr in j1Body:
	    corr.set("rcut","5")
	j3Body= wavefunc[3]
	for corr in j3Body:
	    corr.set("rcut","3")
except Exception:
	print "There are no jastrows in the wavefunction"


###### NOW WRITE THE MODIFICATIONS TO A FILE
tmpfile = myfile+".tmp"
f = open( tmpfile,"w")
f.write("<?xml version=\"1.0\"?>\n")
f.write(etree.tostring(root,pretty_print=True))
f.close()

os.system("mv " + tmpfile + " " + myfile)

os.system("./cusp.sh")
