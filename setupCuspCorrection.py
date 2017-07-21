def generate_CuspDir(outerDir,fileroot,multiDet,filePath):
	### following can be undone to revert to executable
	'''
	#!/usr/bin/env python 
	# -*- coding : utf-8 -*- 

	import os, sys

	outerDir = sys.argv[1]

	## fileroot is the absolute path to this file
	fileroot = sys.argv[2]
	multiDet=sys.argv[3]
	filePath = sys.argv[4]

	'''

	import lxml
	from lxml import etree
	thisDir = outerDir + "/CuspCorrection"

	if not(os.path.isdir(thisDir)):
		os.mkdir(thisDir)

	os.system("cp " + filePath + "misc/Cusp.xml " +thisDir)


	myFile = thisDir+"/Cusp.xml"
	tree = etree.parse(myFile)
	## Modify Cusp.xml for your system

	root = tree.getroot()

	project = root[0]
	icld_ptcl = root[2]
	icld_wfs = root[3]

	project.set("id",fileroot)

	ptclFile = fileroot+".ptcl.xml"
	wfsFile =  fileroot+".wfs.xml"
	icld_ptcl.set("href",ptclFile)
	icld_wfs.set("href",wfsFile)

	###### NOW WRITE THE MODIFICATIONS TO A FILE
	tmpfile = myFile+".tmp"
	f = open( tmpfile,"w")
	f.write("<?xml version=\"1.0\"?>\n")
	f.write(etree.tostring(root,pretty_print=True))
	f.close()

	os.system("mv " + tmpfile + " " + myFile)


	if multiDet:
	    fileName = "modify_wfs_4_Cusp_multi.py"
	else:
	    fileName = "modify_wfs_4_Cusp_single.py"
	
	os.system("cp "+filePath +"misc/"+fileName+" "+thisDir+"/modify_wfs_4_Cusp.py")
	
	os.system("cp "+filePath +"misc/cusp.sh " +thisDir + "/cusp.sh") 
	

