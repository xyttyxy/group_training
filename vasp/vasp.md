# VASP related stuff
This document provides information on compiling and using vasp
## Compiling
General instructions for compiling are found in the source folder, which you should already have if you're reading this. More information is found on the [manual](https://www.vasp.at/wiki/index.php/Installing_VASP.5.X.X). Conceptually, you will need: 
- A suite of Fortran, C++, and C compilers. 

On most platforms you will have Intel and GNU compilers, occasionally others (e.g. AOCC and LLVM) are used. Typically cluster administrator provide detailed documentation on selecting and using them. 
- An installation of message passing interface (MPI). 

The MPI is a set of standard communicaiton protocols for programs running on different CPUs to communicate with each other and coordinate their computing efforts. VASP is almost always run as a highly parallized application, so it is necessary that appropriate MPI is available and selected. 
- Linear algebra libraries. As DFT is basically solving an eigenvalue problem, the heavylifting is performed by linear algebra libraries. 
- Fast Fourier Transform (FFT) library. 

All these are controlled via the makefile.include file in the source folder, and the module environment variable management tool. You should have learned what environment variables are and how to view and update them. `module.sh` is just a convenient automation tool for this and is available on all the clusters. Loading appropriate modules ensure the compilers and linkers can find the appropriate definitions of symbols in building the application. To learn how to use it, go to the [documentation](http://modules.sourceforge.net/). Specific module names can be found by typing

    module avail
	
In principle the compiler, MPI, and the numerical libraries can be mixed and matched, but in practice compatibility is poor and one has to resort to trial and error to find which combinations work the best (fast and stable). This repository provides example files that were tested to work on some clusters the group use. 
 - UCLA [Hoffman2](./makefile.include.hoff)
 - SDSC [Expanse](./makefile.include.expanse.vasp5)
 - PSC [Bridges2](./makefile.include.br2)

Simply download them to the src folder, rename to `makefile.include`, load the appropriate modules (indicated in file), and `make all`.

## Tutorials and Examples
## Errors and Debugging


