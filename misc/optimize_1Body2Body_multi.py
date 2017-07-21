#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
	import os 
        import lxml
        from lxml import etree
	import sys

	fileroot = sys.argv[1]
        myfile ="../"+fileroot+".wfs.xml"
	os.system("cp "+ myfile +" " +myfile + "_BAK")

	tree= etree.parse(myfile)
	root = tree.getroot()
	wavefunc = root[0]
	determinantset = wavefunc[0]
	multidet = determinantset[3]
	multidet.set("optimize","no")
	
	j2Body= wavefunc[1]
	j1Body= wavefunc[2]
	for corr in j2Body:
            corr.set("rcut","10")
	for corr in j1Body:
            corr.set("rcut","5")
        j3Body= wavefunc[3]
	for corr in j3Body:
	    corr.set("rcut","3")
            corr[0].set("optimize","no")
	
	###### NOW WRITE THE MODIFICATIONS TO A FILE
	tmpfile = myfile+".tmp"
	f = open( tmpfile,"w")
	f.write("<?xml version=\"1.0\"?>\n")
	f.write(etree.tostring(root,pretty_print=True))
	f.close()

	os.system("mv " + tmpfile + " " + myfile)
	
except Exception:
	print "Please check filenames and existence of files" 
else:
	print "Submitting Optimization of 1 and 2 body Jastrows"
        os.system("./bgq-Opt.sh")
	
