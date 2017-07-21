# qmcpack_input_generator
Takes a file from quantum package that is ready for conversion (i.e. save_for_qmcpack has been used) and generates the *wfs.xml, *ptcl.xml, DMC folder, and Optimization folder. 


## Uses
   ./setup_QMC_calculation.py setup --filename=<filename.ext> --method=<QP> 		
                                   [--noJastrow=<True,False>]
			                             [--3BodyJ=<True,False>]
			                             [--reoptimizeCoeffs=<True,False>]
                                   
                    Filename: the file that is ready for conversion to qmcpack
                    Method: at the moment only quantum package input can be used, but it would be relatively easy to modify the setupMethods.py file if another input is desired.
                    --noJastrow= default is false. Set to true if you do NOT want 1,2, or 3 body jastrow
                    --3BodyJ   =default is True. Set to false if you only want 1 and 2 body Jastrows.
                    --reoptimizeCoeffs = default is False. Set to true if you want to reoptimize multideterminant coefficients
                 
### Output 
    This script can be called from the directory with the input file and generates all needed input for QMC.
    The *wfs.xml and *ptcl.xml files will be generated in a subdirectory called JASTROW_NDET(_reopt).
    If any optimization will take place the Optimization folder will be created with the appropriate scripts inside. 
    A DMC folder will be created with the needed files. 
    The Hamiltonians in each are created based on whether a pseudopotential was used. 
    If it's an all-electron calculation then a Cusp Correction folder will be created.
    
    For single determinant calculations: Only main directory will be generated
    For mulit determinant  calculations: Withint the main directory there will be cutoff directories containing the Optimization and/or DMC folders.
   
   
### Example of use

       cd myTest
       pwd 
           ~/myTest
       ls
           thisSystem.dump
	   
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
	     bgq-DMC.sh   DMC.xml   format_data.py
	     
	ls Jastrow123_Multi/cutoff_VALUE/Optimization/
	   
	    
