# qmcpack_input_generator
Takes a file from quantum package that is ready for conversion (i.e. save_for_qmcpack has been used) and generates the *wfs.xml, *ptcl.xml, DMC folder, and Optimization folder (defaulting to adding only the 1 and 2 body Jastrows). 


## Uses
   ./setup_QMC_calculation.py setup --filename=<filename.ext> --method=QP  [--noJastrow=<True,False>]
			                             [--3BodyJ=<True,False>]
			                             [--reoptimizeCoeffs=<True,False>]
                                   
                    Filename: the file that is ready for conversion to qmcpack
                    Method: at the moment only quantum package input can be used, but it would be relatively easy to modify the setupMethods.py file if another input is desired.
                    --noJastrow= default is false. Set to true if you do NOT want 1,2, or 3 body jastrow
                    --3BodyJ   =default is False. Set to false if you only want 1 and 2 body Jastrows.
                    --reoptimizeCoeffs = default is False. Set to true if you want to reoptimize multideterminant coefficients
		    
### Output 
    This script can be called from the directory with the input file and generates all needed input for QMC.
    The *wfs.xml and *ptcl.xml files will be generated in a subdirectory called JASTROW_NDET(_reopt).
    If any optimization will take place the Optimization folder will be created with the Opt.xml file (The Opt.xml file is either misc/Opt_AE.xml or a version of misc/Opt_PP.xml with the proper pseudopotential Hamiltonian). 
    A DMC folder will be created with the needed DMC.xml file (The DMC.xml file is either misc/DMC_AE.xml or a version of misc/DMC_PP.xml with the proper pseudopotential Hamiltonian). 
    The Hamiltonians in each are created based on whether a pseudopotential was used. 
    If it's an all-electron calculation then a Cusp Correction folder will be created.
    
    For single determinant calculations: Only main directory will be generated
    For mulit determinant  calculations: Within the main directory there will be cutoff directories containing the Optimization and/or DMC folders.
 
### 
   
### Example of use

       cd myTest
       pwd 
           ~/myTest
       ls
           thisSystem.dump
	   
	   
##Running within the generated directories using the generated files
	                
	
	   
       ~/qmcpack_input_generator/setup_QMC_calculation.py setup --filename=thisSystem.dump --method=QP --3BodyJ=True
       
	'''We have received all needed info
		do_psuedo =  False
		The file is from quantum package
		The input files will be place in  Jastrow123_MultiDet
		Beginning conversion
		Rank =    0  Free Memory = 13699 MB
		Finished Conversion
		Multi reference system
		This is an all electron calculation so the Cusp correction is being added
		setupMethod.py is done
		Everything is done
		'''
	ls
	     thisSystem.dump     conversion.out     Jastrow123_Multi
	ls Jastrow123_Multi/
	     thisSystem.wfs.xml    thisSystem.ptcl.xml    CuspCorrection  DMC/   Optimization/
	
	ls Jastrow123_Multi/DMC/
	     DMC.xml
	     
	ls Jastrow123_Multi/Optimization/
	     Opt.xml

# qmcpack optimizer files


   ./optimize_system.py --optFile optFile.xml --wfsFile wfsFile.xml --optType {}

	optFile: The name of optimization file that will be used ( It should already exist in the directory)
	wfsFile: The name of wavefunction file that will be used 
	optType: 
		 12 -> optimize 1 and 2 body Jastrows only
		 RC -> include the coefficient reoptimization
		 3B -> include the 3 body Jastrow in the optimization
		 Fin -> check to see if the system is ready for DMC
   
	
	This file checks the energies and makes a guess whether optimization is occuring based on if the previous energy is decreasing
	( it looks at the minimum energy of the current group and if that is less than the average for the previous group it continues the optimization)
	
	It also outputs "opt_run_info.dat" to help keep track of which optimization type was done for which group of files

## What the script does internally
	1) It goes through the input arguments and checks that a valid optimization and wavefunction file are given. It then checks that an optimization type is given.
	2) It checks which *opt.xml files have been output and sets the restart number as the last *.opt.xml +1
	3) It opens the optimization file and checks where the group started and then sets the series number as the restart number. It also pulls the project id for later use.
	4) If an optimization run has been done, it sends the qmca data into "opt_energy_qmca.dat". It will then grab the energies and associated series number from that file.
	5) If no optimization run has been done, it will generate the "opt_run_info.dat" file. If only one run has been done, it will initialize the data. If mulitple runs have been done, then it will pull information from the file (the most important is the Echeck value).
	6) The wavefunction file is backed up, and if there has been an optimization run the best wavefunction will replace it
	7) It looks at the wavefunction and determines which optimizations have been done ( for output to "opt_run_info.dat")
	8) If the wavefunction needs to be modifies (i.e. the first step in optimization is needed or we are moving to the next optimization step), then it is changed based on user input (i.e. the value of optType)
	9) If we have overwritten the wavefunction file with a series optimziation file, then we add a comment into the main wavefunction file which specifies the series number.
	10) If the opt_run_info data exists, then it is output to the file 
	11) Finally, if no errors occured, then the modified optimization file replaces the original optimization file and the modified wavefunction file replaces the original wavefunction file. (If an error occurs, then the modified files may exist as "Filename.ext.tmp")

## output files
	opt_energy_qmca.dat: holds the qmca output 
	opt_run_info.dat: type of optimization, the run number (for saving wavefunction files), Echeck (used for making sure the next set of energies are decreasing),series number for start of the group
