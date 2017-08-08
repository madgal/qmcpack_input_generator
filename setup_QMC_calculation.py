#!/usr/bin/env python
# -*- coding: utf-8 -*-


## This code generates input to QMCPack by using quantum_package code

""" 
Usage: 
  setup_QMC_calculation.py (-h | --help)
  setup_QMC_calculation.py setup --filename=<filename.ext>
			--method=<QP>
			[--noJastrow=<True,False>]
			[--3BodyJ=<True,False>]
			[--reoptimizeCoeffs=<True,False>]

Example of use:
	./setup_QMC_calculation.py setup  --filename=qp_dumpfilename --method=QP --reoptimizeCoeffs=True
"""

### defaults to adding 3BodyJ

try:
    import os
    import sys
    thispath = os.path.abspath(sys.argv[0])
    thispath = thispath.replace("setup_QMC_calculation.py","")
    ## add the paths to the system so it is easier to find the location of the needed files
    sys.path.insert(0, thispath)
    sys.path.insert(0, thispath+"misc/")
    sys.path.insert(0, thispath+"src/")

    import setupMethods 
    ### docopt allows the easy argument usage
    from docopt import docopt
    version="0.0.1"
except:
    print "File is corupted. Git reset may fix the issues"
    sys.exit(1)

def main():

    arguments = docopt(__doc__, version='G2 Api ' + version)


    ### Retrieve the arguments passed by the user
    if not (arguments["--filename"] and arguments["--method"]):
	print "The filename and conversionType are required"
	sys.exit(1)
    else:
	filename= arguments["--filename"]
	method  = arguments["--method"]

	## Default is 1 and 2 body jastrow, no reoptimization of coefficients
	if arguments["--noJastrow"]:
		nojastrow = arguments["--noJastrow"]=="True"
	else:
		nojastrow = False

	if arguments["--3BodyJ"]:
		use3Body = arguments["--3BodyJ"]=="True"
	else:
		use3Body = False
	if arguments["--reoptimizeCoeffs"]:
		reopt = arguments["--reoptimizeCoeffs"]=="True"
	else:
		reopt=False

	if method=="QP":
		necessaryInfo = setupMethods.useQuantumPackageMethod(filename)

	#elif method=="":
		#necessaryInfo = setupMethods.useOtherMethod(filename)

	[elementList,numDet,convertType,doPseudo,multidet,fileroot] = necessaryInfo

	'''
	Now we begin the building of the necessary directories
		and add the flags needed when using "convert4qmc"
	'''
	dirName =""
	flags=""
	if nojastrow:
		dirName=dirName+"NoJastrow_"
		flags = flags+ " -nojastrow "
	elif use3Body:
		dirName=dirName+"Jastrow123_"
		flags = flags+" -add3BodyJ "
	else:
		dirName=dirName+"Jastrow12_"

	if multidet:
		dirName = dirName +"MultiDet"
	else:
		dirName = dirName +"1Det"
	if reopt:
		dirName = dirName + "_reopt"


	if not(os.path.isdir(dirName)):
		os.mkdir(dirName)
	local_fileroot = dirName +"/"+fileroot
	print "The input files will be place in ",dirName

	if doPseudo:
	    for el in elementList:
			pseudoDir=dirName
			## retrieve the pseudopotential from the qmcpack directory so it's in xml format
			#os.system("cp /soft/applications/qmcpack/pseudopotentials/BFD/"+el + ".BFD.xml " + pseudoDir)
			os.system("cp ~/qmcpack-3.0.0/pseudopotentials/BFD/"+el + ".BFD.xml " + pseudoDir)
	else:
		pseudoDir=False
		## if its all electron then also add the Cusp condition
		flags = flags +" -addCusp "


	print "Beginning conversion"
	do_conversion(convertType,filename,local_fileroot,flags)
	print "Finished Conversion"

	

	### the files should be in one of the paths which we appended 
	### so that we could find the files when we executed them outside the
	### directory containing them 
	### get a few needed variables for the setup
	absfileroot = os.getcwd() + "/"+dirName + "/"+ fileroot
	for trypath in sys.path:
		if os.path.exists(trypath+"setup_QMC_calculation.py"):
			filePath = trypath
			break


	if not(doPseudo):
		print "This is an all electron calculation so the Cusp correction is being added"
		ogDir = os.getcwd()
		os.chdir(dirName)
		generate_CuspDir(absfileroot,absfileroot,filePath,multidet)
		os.chdir(ogDir)

	if multidet:
		print "Multi reference system"
		### this will call another program which will generate
		### cutoff directories containing 
		### optimization and DMC folders
		generateCutoff(dirName,absfileroot,fileroot,pseudoDir,elementList,filePath)
		
	else:
		print "Single reference system"
		### generate the DMC and Optimization folders
		#import setupDMCFolder
		#setupDMCFolder.makeFolder(dirName,absfileroot,absfileroot,fileroot,doPseudo,elementList,filePath)
		ogDir = os.getcwd()
		os.chdir(dirName)
		createStepFolder(absfileroot,absfileroot,pseudoDir,elementList,"DMC",filePath)
		createStepFolder(absfileroot,absfileroot,pseudoDir,elementList,"Opt",filePath)
		os.chdir(ogDir)
		#import setupOptFolder
		#setupOptFolder.makeFolder(dirName,absfileroot,absfileroot,fileroot,doPseudo,elementList,filePath)
def do_conversion(method,dumpfile,filename,flags):
	import os 
	#BINDIR ="/soft/applications/qmcpack/github/build_Intel_real/bin"
	BINDIR ="~/qmcpack-3.0.0/build/bin"

	os.system(BINDIR+"/convert4qmc -"+method+" "+dumpfile +" "+ flags )
	os.rename("sample.Gaussian-G2.xml",filename+".wfs.xml")
	os.rename("sample.Gaussian-G2.ptcl.xml",filename+".ptcl.xml")

def createStepFolder(ptclfileroot,wfsfileroot,pseudoDir,elementList,step,filePath):
	
	import os
	################################################
	#### Generate : DMC.xml
	################################################
	import lxml
	from lxml import etree

	if pseudoDir:
	    template_Name = step+"_PP.xml"
	else:
	    template_Name = step+"_AE.xml"
	    
	this_dir = step
	if not(os.path.isdir(this_dir)):
	    os.mkdir(this_dir)
	os.system("cp " + filePath + "misc/"+template_Name+" " +this_dir+"/"+step+".xml")
	
	
	myFile = this_dir+"/"+step+".xml"
	tree = etree.parse(myFile)
	root = tree.getroot()
	
	project = root[0]
	icld_ptcl = root[2]
	icld_wfs = root[3]
	
	if pseudoDir:
		hamilt   = root[5] 
		pairPot1 = hamilt[0]
	
		count=0
		for el in elementList:
			pairPot1.append(etree.Element("pseudo"))
        		pseudo = pairPot1[count]
			pseudo.set("elementType",el)
			el_path = os.path.abspath(el+".BFD.xml")
	
			pseudo.set("href",el_path)
			count+=1

	## get the rootname to use as the project id
	filename = ptclfileroot.split("/")[-1]
	filename = filename.split(".")[0]
		
	projName = step+"-"+filename
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
	
	#os.system("cp " +filePath + "misc/bgq-"+step+".sh "+this_dir)
		
def generateCutoff(thisDir,absfileroot,fileroot,pseudoDir,elementList,filePath):
	import os
	cutoffs = [0.01,0.008,0.006,0.004,0.002,0.0009,0.0007,0.0005,0.0003,0.0001,0.00008,0.00006,0.00004]

	for value in cutoffs:

		cutoffDir = thisDir +"/cutoff_"+str(value)
		if not(os.path.isdir(cutoffDir)):
			os.mkdir(cutoffDir)
		wfs_fileroot = fileroot+"_"+str(value)


		wfsFilename=wfs_fileroot+".wfs.xml"
		wfsFilename = os.path.abspath(cutoffDir + "/"+wfsFilename)
		os.system("cp "+absfileroot+".wfs.xml " + wfsFilename)
		modify_wfs(wfsFilename,"Cutoff",True,value)

		abs_wfsfile = wfsFilename
		ogDir = os.getcwd()
		os.chdir(cutoffDir)
		createStepFolder(absfileroot,abs_wfsfile,pseudoDir,elementList,"DMC",filePath)
		createStepFolder(absfileroot,abs_wfsfile,pseudoDir,elementList,"Opt",filePath)
		os.chdir(ogDir)
def generate_CuspDir(ptclfileroot,wfsfileroot,filePath,multidet):
	### following can be undone to revert to executable
	import os
	import lxml
	from lxml import etree

	thisDir = "CuspCorrection"
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

	project.set("id",ptclfileroot.split("/")[-1])

	ptclFile = ptclfileroot+".ptcl.xml"
	wfsFile =  wfsfileroot+".wfs.xml"
	icld_ptcl.set("href",ptclFile)
	icld_wfs.set("href",wfsFile)

	###### NOW WRITE THE MODIFICATIONS TO A FILE
	tmpfile = myFile+".tmp"
	f = open( tmpfile,"w")
	f.write("<?xml version=\"1.0\"?>\n")
	f.write(etree.tostring(root,pretty_print=True))
	f.close()

	os.system("mv " + tmpfile + " " + myFile)

	modify_wfs(wfsFile,"Cusp",multidet)

	#os.system("cp "+filePath +"misc/cusp.sh " +thisDir + "/cusp.sh") 

def modify_wfs(myfile,modType,multi,cutoff=0.01):
	import os 
	import lxml
	from lxml import etree

	if modType=="Cusp":	

		os.system("cp "+myfile+" " + myfile+"_initial")

		tree= etree.parse(myfile)
		root = tree.getroot()
		wavefunc = root[0]
		determinantset = wavefunc[0]
		fulldir=os.getcwd()

		if multi:
			sposet_up = determinantset[1]
			sposet_dn = determinantset[2]
			MyCuspUp=fulldir+"/CuspCorrection/spo-up.cuspInfo.xml"
			sposet_up.set("cuspInfo",MyCuspUp)
			MyCuspDn=fulldir+"/CuspCorrection/spo-dn.cuspInfo.xml"
			sposet_dn.set("cuspInfo",MyCuspDn)

		else:
			up_det =  determinantset[1][0]
			dn_det = determinantset[1][1]
			MyCuspUp =fulldir+"/CuspCorrection/updet.cuspInfo.xml"
			up_det.set("cuspInfo",MyCuspUp)
			MyCuspDn =fulldir+"/CuspCorrection/downdet.cuspInfo.xml"
			dn_det.set("cuspInfo",MyCuspDn)

	
		###### NOW WRITE THE MODIFICATIONS TO A FILE
		tmpfile = myfile+".tmp"
		f = open( tmpfile,"w")
		f.write("<?xml version=\"1.0\"?>\n")
		f.write(etree.tostring(root,pretty_print=True))
		f.close()
		
		os.system("mv " + tmpfile + " " + myfile)

	elif modType=="Cutoff":
		match = "<ci id="
	        match =match.replace(" ","")
        	qc_match = "qc_coeff="

	        tmpFilenam = myfile +".tmp"
                tmpFile = open(tmpFilenam,"w")
        	dets=0
        	with open (myfile,"r") as fileIn:
                        for row in fileIn:
                	        line = row.replace(" ","")
                	        if line[0:3] ==match[0:3]:
                                        line = row.split(" ")
                        	        for el in line:
                        	                if el[0:8] == qc_match[0:8]:
                                                        if abs(float(el[10:-1])) >= cutoff:
                                	                        tmpFile.write(row)
                                	                        dets+=1
                                                        break

	                        else:
	                                tmpFile.write(row)
        
        	tmpFile.close()
        	os.system("mv " + tmpFilenam + " " +myfile)
                

                tree = etree.parse(myfile)
                root = tree.getroot()
                wavefunc = root[0]
                determinantset = wavefunc[0]
                multidet = determinantset[3]
                multidet[0].set("size",str(dets))
                multidet[0].set("cutoff",str(cutoff))

                f = open(tmpFilenam,"w")
                f.write("<?xml version=\"1.0\"?>\n")
                f.write(etree.tostring(root,pretty_print=True))
                f.close()

        	os.system("mv " + tmpFilenam + " " +myfile)	

#### Now call the main function to generate everything
main()
