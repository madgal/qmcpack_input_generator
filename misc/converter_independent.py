def do_conversion(method,dumpfile,filename,flags):
	### the following can be used if you want to revert this to an executable
	'''
	#!/usr/bin/env python 
	# -*- coding: utf-8 -*- 
	#THIS FILE CONVERTS FOR QMCPACK INPUT 
	import sys

	method=sys.argv[1]
	dumpfile = sys.argv[2]
	filename = sys.argv[3]
	flags = sys.argv[4]
	'''

	import os 
	#BINDIR ="/soft/applications/qmcpack/github/build_Intel_real/bin"
	BINDIR ="~/qmcpack-3.0.0/build/bin"

	os.system(BINDIR+"/convert4qmc -"+method+" "+dumpfile +" "+ flags + " > conversion.out" )
	os.rename("sample.Gaussian-G2.xml",filename+".wfs.xml")
	os.rename("sample.Gaussian-G2.ptcl.xml",filename+".ptcl.xml")

	
