def useQuantumPackageMethod(filename):
	'''
	 The function that will take the dump file from quantum package
		 and  returns the needed information to the main function
	'''
	import sys

	readEl=False
	elementList=[]
	numDetMatch = "Number of determinants"
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
				## we have finished reading in the element list 
				## and all other needed information
				break
			elif readEl:
				## add all elements so that there are no repeated elements
				## this is needed if there is a pseudopotential
				newEl =line.split(" ")[0]
				if newEl not in elementList:
					elementList.append(str(newEl))

	## Do a couple checks that should return false and allow the qmcpack file to finish
	if convertType !="QP":
		print "There is an error: Are you sure this was generated with quantum package?"
    		sys.exit(1)

	elif (multidet and numDet==1) or ( numDet > 1 and not(multidet)):
		print "There was an error: The number of determinants does not match with the multi/single reference system"
		sys.exit(1)
	else:
		print "The file is from quantum package\n All needed info has been obtained"


	fileroot = filename.split('.')[0]
	
	return [elementList,numDet,convertType,doPseudo,multidet,fileroot]

	print "All info from the quantum package file has been found"

###################################################################3
'''
def useOtherMethod(filename):
	#A template definition for adding additional methods
	import sys

	
	## read in the file
	with open(filename, "r") as fileIn:
		for line in fileIn:	
			# get the info
			elementList=[]# the elements in the system (none repeated)
			numDet=1#the number of determinants 
			convertType="MethodNameForQmcpackConverter"# for use in convert4qmc
			doPseudo=True # determine from file and not user input			
			multidet=False # determine from file or numDet
	
	if convertType !="MethodNameForQmcpackConverter":
		print "There is an error: Are you sure this was generated with the other method?"
    		sys.exit(1)

	elif otherCheck:
		print "There is an error: Check this ..."
		sys.exit(1)

	else:
		print "The file is from the other method\n All needed info has been obtained"
		
	fileroot = filename.split('.')[0]
	return [elementList,numDet,convertType,doPseudo,multidet,fileroot]

	print "All info from the file has been found"
'''

