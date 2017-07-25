def makeFolder(outerDir,ptclfileroot,wfsfileroot,filename,usepp,elementList,filePath):
	"""
	#!/usr/bin/env python
	# -*- coding: utf-8 -*- 
	import sys
	
	outerDir=sys.argv[1]
	ptclfileroot=sys.argv[2]
	wfsfileroot=sys.argv[3]
	filename = sys.argv[4]
	usepp = sys.argv[5]
	elementList = sys.argv[6]
	filePath = sys.argv[7]
	
	"""
	import os
	################################################
	#### Generate : Opt.xml
	################################################
	import lxml
	from lxml import etree
	
	
	info = outerDir.split("/")

	for piece in info:
		if "Jastrow" in piece:
			info = piece
			break
	info = info.split("_")
	#print info
	if len(info)==3:
		[Jtype, multi,reopt] = info
		reopt = reopt=="reopt"
	else:
        	[Jtype, multi] = info
		reopt=False
		
	Jtype = Jtype.replace("Jastrow","")
	multi = multi=="MultiDet"
	
	if Jtype!="No":

		if usepp:
		    template_Name = "Opt_PP.xml"
		else:
		    template_Name = "Opt_AE.xml"
	    
		Opt_dir = outerDir + "/Optimization"
		if not(os.path.isdir(Opt_dir)):
		    os.mkdir(Opt_dir)
		os.system("cp " + filePath +"misc/"+template_Name+" " +Opt_dir+"/Opt.xml")
		os.system("cp " + filePath +"utils/plot_OptProg.py " +Opt_dir)
	
		myFile = Opt_dir+"/Opt.xml"
		tree = etree.parse(myFile)
		root = tree.getroot()
	
		if usepp:
			hamilt   = root[5] 
			pairPot1 = hamilt[0]
	
			## remove the bracket from the beginning and end then 
			## parse by comma to get it back into list format
			elementList = elementList.replace("[","")
			elementList = elementList.replace("]","")
			elementList = elementList.split(",")
		
        
	
	
			count=0
			for el in elementList:
				#os.system("cp /soft/applications/qmcpack/pseudopotentials/BFD/"+el + ".BFD.xml " + outerDir)
				os.system("cp ~/qmcpack-3.0.0/pseudopotentials/BFD/"+el + ".BFD.xml " + outerDir)
	
				pairPot1.append(etree.Element("pseudo"))
				pseudo = pairPot1[count]
				pseudo.set("elementType",el)
				el_path = os.path.abspath(outerDir+ "/"+el+".BFD.xml")
				pseudo.set("href",el_path)
				count+=1
		
		project = root[0]
		icld_ptcl = root[2]
		icld_wfs = root[3]
	
		projName = "Opt-"+filename
		project.set("id",projName)
	
		ptclFile = ptclfileroot +".ptcl.xml"
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
		
		################################################
		### Generate bgq-DMC.sh
        	################################################
		os.system("cp " + filePath + "misc/bgq-Opt.sh "+outerDir+"/Optimization/")
	
		os.system("cp " + filePath + "misc/optimize_1Body2Body.py "+Opt_dir)
		    
		if reopt:
			os.system("cp " + filePath + "misc/optimize_and_include_coeffs.py "+Opt_dir)
	
		if "3" in  Jtype:
			os.system("cp " + filePath + "misc/optimize_and_include_3Body.py "+Opt_dir)
	
		os.system("cp " + filePath + "misc/finish_optimization_and_setup_wfs_4_DMC.py "+Opt_dir)
	
