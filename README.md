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
	     thisSystem.wfs.xml    thisSystem.ptcl.xml    CuspCorrection   cutoff_VALUE/
	
	ls Jastrow123_Multi/cutoff_VALUE/
	     thisSystem_VALUE.wfs.xml  thisSystem.ptcl.xml   DMC/   Optimization/
	
	ls Jastrow123_Multi/cutoff_VALUE/DMC/
	     DMC.xml
	     
	ls Jastrow123_Multi/cutoff_VALUE/Optimization/
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
