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

  ./optimize_1Body2Body.py  wfsFileroot
          
	  wfsFileroot: The name of the wavefunction file (not an absolute path) and is expected to be in the previous directory (i.e the wavefunction file is  "../wfsFileroot.wfs.xml")
	  This will change all the Jastrow values to: 
	  		J2 -> rcut=10
			J1 -> rcut=5
			J3 -> rcut=3, optimize="no"
	  Also, if it is a multideterminant it sets optimize="no"
	  
   ./optimize_and_include_coeffs.py wfsFileroot
   
   	wfsFileroot: The name of the wavefunction file (not an absolute path) and is expected to be in the previous directory (i.e the wavefunction file is  "../wfsFileroot.wfs.xml" )
		This will check that the energy has not grown (i.e. the wavefunction is being optimized correctly) 
		If the energy is reducing, it will then make a backup of the previous wavefunction and copy the Opt-wavefunction with the lowest energy to the wfs.xml file (the energies used to determine this are output to file "opt_1b2b.dat")
		It will update the series start in the Opt.xml file
		And set multideterminant optimize="yes"

    ./optimize_and_include_3Body.py wfsFileroot
    
    	wfsFileroot: The name of the wavefunction file (not an absolute path) and is expected to be in the previous directory (i.e. the wavefunction is "../wfsFileroot.wfs.xml")
		This will check that the energy has not grown (i.e. the wavefunction is being optimized correctly)
		If the energy is reducing, it will then make a backup of the previous wavefunction and copy the Opt-wavefunction with the lowest energy to the wfs.xml file (the energies used to determine this are output to file "opt_without3Body.dat")
		It will update the series start in the Opt.xml file
		And set J3 optimize="yes"

   ./finish_optimization_and_setup_wfs_4_DMC.py
   
         wfsFileroot: The name of the wavefunction file (not an absolute path) and is expected to be in the previous directory (i.e. the wavefunction is "../wfsFileroot.wfs.xml")
	 	This will check that the energy has not grown (i.e. the wavefunction is being optimized correctly)
		If the energy is reducing, it will then make a backup of the previous wavefunction and copy the Opt-wavefunction with the lowest energy to the wfs.xml file (the energies used to determine this are output to file "opt_final.dat") 
		Once this is finished the system is ready for a DMC run
	
### Notes
	These files can be executed in the same way as the setup file by doing 
	Also, if the system is very difficult to optimize you may want to do a quick check before submitting the optimization run to ensure the correct portions are getting optimized
	~/qmcpack_input_generator/{put_the_filename_here}.py
