def modify_wfs_4_cutoff(cutoffDir,thisDir,initfileroot,wfsfileroot,value):
	'''
 	This function takes a wavefunction in the current directory 
 	  and copies it to the cutoff directory.
 	  It will then remove the determinants with coefficients 
 	  below the cutoff value.
	'''
	import os

	newfilename=cutoffDir +"/"+wfsfileroot

	initFile = thisDir +"/" +initfileroot
        os.system("cp "+initFile+".wfs.xml "+newfilename+".wfs.xml")
        os.system("cp "+initFile+".ptcl.xml "+cutoffDir+"/")


        match = "<ci id="
        match =match.replace(" ","")
        qc_match = "qc_coeff="

	cutoffroot =  newfilename +".wfs.xml"
        tmpFilenam = cutoffroot +".tmp"
        tmpFile = open(tmpFilenam,"w")
        dets=0
        with open (cutoffroot,"r") as fileIn:
                for row in fileIn:
                        line = row.replace(" ","")
                        if line[0:3] ==match[0:3]:
                                line = row.split(" ")
                                for el in line:
                                        if el[0:8] == qc_match[0:8]:
                                                if abs(float(el[10:-1])) >= value:
                                                        tmpFile.write(row)
                                                        dets+=1
                                                break

                        else:
                                tmpFile.write(row)

        tmpFile.close()
        os.system("mv " + tmpFilenam + " " +cutoffroot)


        import lxml
        from lxml import etree

        tree = etree.parse(cutoffroot)
        root = tree.getroot()
        wavefunc = root[0]
        determinantset = wavefunc[0]
        multidet = determinantset[3]
        multidet[0].set("size",str(dets))
        multidet[0].set("cutoff",str(value))

        f = open(tmpFilenam,"w")
        f.write("<?xml version=\"1.0\"?>\n")
        f.write(etree.tostring(root,pretty_print=True))
        f.close()

        os.system("mv " + tmpFilenam + " " +cutoffroot)
