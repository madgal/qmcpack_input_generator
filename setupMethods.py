def useQuantumPackageMethod(filename,nojastrow,use3Body,reopt):
	'''
	 The function that will take the dump file from quantum package
		 and generate the needed files to run QMC with qmcpack
	'''
	import os,sys

	readEl=False
	elementList=[]
	numDetMatch = "Number of determinants"
	dirName =""
	flags=""
	if nojastrow:
		dirName=dirName+"NoJastrow_"
		flags = flags+ "-nojastrow "
	elif use3Body:
		dirName=dirName+"Jastrow123_"
		flags = flags+"-add3BodyJ "
	else:
		dirName=dirName+"Jastrow12_"
	with open(filename, "r") as fileIn:
		for line in fileIn:
			if  numDetMatch in line:
				line = line[len(numDetMatch)+2:]
				numDet = int(line)
			elif "QMCPACK" in line:
				line = line[1:]
				line = line.split("->")
				convertType = line[0].replace(" ","")
			elif "do_pseudo" in line:
				line=line.split(" ")
				doPseudo=line[1][0].lower()=="t"
			elif "multi_det" in line:
				line=line.split(" ")
				multidet=line[1][0].lower()=="t"
			elif "Atomic coord in Bohr" in line:
				readEl=True
        
			elif readEl and ("BEGIN_BASIS_SET" in line):
				break
        
			elif readEl:
				newEl =line.split(" ")[0]
				if newEl not in elementList:
					elementList.append(str(newEl))
	print "We have received all needed info"


	if convertType !="QP":
		print "There is an error: Are you sure this was generated with quantum package?"
    		sys.exit(1)

	else:
		print "The file is from quantum package"
		
	#print numDet
	#print convertType
	#print doPseudo
	#print multidet


	fileroot = filename.split('.')[0]
	#print fileroot

	if not(doPseudo):
		flags = flags +"-addCusp "

	if multidet:
		dirName = dirName +"MultiDet"
	else:
		dirName = dirName +"1Det"
	if reopt:
		dirName = dirName + "_reopt"

	
	os.mkdir(dirName)
	local_fileroot = dirName +"/"+fileroot
	print "The input files will be place in ",local_fileroot,".ext"

	#os.system("./misc/converter_independent.py "+convertType+" "+ filename+" "+ local_fileroot+" "+ flags)
	import converter_independent
	print "Beginning conversion"
	converter_independent.do_conversion(convertType,filename,local_fileroot,flags)
	print "Finished Conversion"

	absfileroot = os.getcwd() + "/"+dirName + "/"+ fileroot


	### the files should be in one of these two paths which we appended 
	### so that we could find the files when we executed them outside the
	### directory containing them 
	trypath1 = sys.path[0]
	trypath2 = sys.path[1]
	if multidet:
		print "Multi reference system"
		### this will call another program which will generate
		### cutoff directories containing 
		### optimization and DMC folders
		for trypath in sys.path:
			if os.path.exists(trypath+"generateCutoffDirs4QMC.py"):
				os.system(trypath+"generateCutoffDirs4QMC.py " + str(dirName) + " " + str(absfileroot) + " "+
						 str(fileroot) + "  " +str(doPseudo) + " " +str(elementList)+" " +str(trypath))
				
				print "File executed"
				filePath = trypath
				break
			else:
				print "File not found in " ,trypath,", so trying again"
		
	else:
		print "Single reference system"
		### generate the DMC and Optimization folders
		for trypath in sys.path:
			if os.path.exists(trypath+"setupDMCFolder.py") and os.path.exists(trypath+"setupOptFolder.py"):
				os.system(trypath+"setupDMCFolder.py " + str(dirName) + " " + str(absfileroot) + " " + str(absfileroot)+" "+
						 str(fileroot) + "  " +str(doPseudo) + " " +str(elementList)+" " +str(trypath))
				os.system(trypath+"setupOptFolder.py "+ str(dirName) + " " + str(absfileroot) + " " + str(absfileroot)+" "+
						 str(fileroot) + "  " +str(doPseudo) + " " +str(elementList)+" " +str(trypath))
				filePath = trypath
				break
	if not(doPseudo):
		#os.system("./misc/setupCuspCorrection.py "+dirName+ " " + absfileroot+" " +multidet)
		print "This is an all electron calculation so the Cusp correction is being added"
		import setupCuspCorrection 
		setupCuspCorrection.generate_CuspDir(dirName,absfileroot,multidet,filePath)
	
	print "setupMethod.py is done"
