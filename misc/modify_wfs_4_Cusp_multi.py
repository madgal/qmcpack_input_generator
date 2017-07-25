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

sposet_up = determinantset[1]
sposet_dn = determinantset[2]

fulldir=os.getcwd()
MyCuspUp=fulldir+"/spo-up.cuspInfo.xml"
sposet_up.set("cuspInfo",MyCuspUp)
MyCuspDn=fulldir+"/spo-dn.cuspInfo.xml"
sposet_dn.set("cuspInfo",MyCuspDn)

###### NOW WRITE THE MODIFICATIONS TO A FILE
tmpfile = myfile+".tmp"
f = open( tmpfile,"w")
f.write("<?xml version=\"1.0\"?>\n")
f.write(etree.tostring(root,pretty_print=True))
f.close()

os.system("mv " + tmpfile + " " + myfile)

os.system("./cusp.sh")
