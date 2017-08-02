#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
	import os 
        import lxml
        from lxml import etree
	import sys

	fileroot = sys.argv[1]
        myfile ="../"+fileroot+".wfs.xml"
	## Backup the wfs file
	os.system("cp "+ myfile +" " +myfile + "_BAK")

	####################################################33
	## Open the main wavefunction file and get it ready for 1 and 2 body optimization
	tree= etree.parse(myfile)
	root = tree.getroot()
	wavefunc = root[0]
	try:
		## if there is a multideterminant make sure to not optimize
		determinantset = wavefunc[0]
		multidet = determinantset[3]
		multidet.set("optimize","no")
	except Exception:
		print "This is a single determinant system"
	else:
		print "This is a multi determinant system"

	## modify the rcut for the 1and 2 body Jastrows
	j2Body= wavefunc[1]
	j1Body= wavefunc[2]
	for corr in j2Body:
            corr.set("rcut","10")
	for corr in j1Body:
            corr.set("rcut","5")
	try:
		## if using a 3 body Jastrow, set rcut to 3 and make sure to not optimize
	        j3Body= wavefunc[3]
		for corr in j3Body:
		    corr.set("rcut","3")
        	    corr[0].set("optimize","no")
	except Exception:
		print "Only 1 and 2 body Jastrows"
	else:
		print "1, 2, and 3 body Jastrows"
	
	###### Now write the modifications to a file
	tmpfile = myfile+".tmp"
	f = open( tmpfile,"w")
	f.write("<?xml version=\"1.0\"?>\n")
	f.write(etree.tostring(root,pretty_print=True))
	f.close()

	os.system("mv " + tmpfile + " " + myfile)
	
except Exception:
	print "Please check filenames and existence of files" 
else:
	print "Check and submit Optimization of 1 and 2 body Jastrows"
	
