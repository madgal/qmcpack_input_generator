def generateCutoff(thisDir,absfileroot,fileroot,doPseudo,elementList,filePath):
	'''
	#!/usr/bin/env python
	# -*- coding: utf-8 -*-
	import sys

	thisDir = sys.argv[1]
	absfileroot = sys.argv[2]
	fileroot = sys.argv[3]
	doPseudo = sys.argv[4]
	elementList = sys.argv[5]
	filePath = sys.argv[6]
	'''

	import os
	import modify_multiDet_wfs4cutoff 
	cutoffs = [0.01,0.008,0.006,0.004,0.002,0.0009,0.0007,0.0005,0.0003,0.0001,0.00008,0.00006,0.00004]

	for value in cutoffs:

		cutoffDir = thisDir +"/cutoff_"+str(value)
		if not(os.path.isdir(cutoffDir)):
			os.mkdir(cutoffDir)
		wfs_fileroot = fileroot+"_"+str(value)


		modify_multiDet_wfs4cutoff.modify_wfs_4_cutoff(cutoffDir,thisDir,fileroot,wfs_fileroot,value)

		abs_wfsfile = absfileroot + "_"+str(value)
		'''
		os.system(filePath+"/setupDMCFolder.py " + str(cutoffDir) + " " + str(absfileroot) + " " + str(abs_wfsfile)+" " +str(fileroot) + "  " +str(doPseudo) + " " +str(elementList)+" " +str(filePath))
		os.system(filePath+"/setupOptFolder.py " + str(cutoffDir) + " " + str(absfileroot) + " " + str(abs_wfsfile)+" " +str(fileroot) + "  " +str(doPseudo) + " " +str(elementList)+" " +str(filePath))

		'''
		import setupDMCFolder
		setupDMCFolder.makeFolder(cutoffDir,absfileroot,abs_wfsfile,fileroot,doPseudo,elementList,filePath)
		import setupOptFolder
		setupOptFolder.makeFolder(cutoffDir,absfileroot,abs_wfsfile,fileroot,doPseudo,elementList,filePath)

