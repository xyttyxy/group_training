# Compiling LAMMPS
LAMMPS is free software and is usually installed on compute clusters. However, clusters installations almost never have all the packages you want and it is often necessary to recompile them. This is fairly straightforward on clusters since all relevant MPI and compilers are installed and optimized. On the other hand, if you would like a local installation for development purposes, some more work is needed. This file documents the steps I took to build a parallelized LAMMPS binary on a Ubuntu laptop, and in making it more usable from python. 

## Installing prereqs
```
sudo apt update
sudo apt install build-essentials # basic compiler, assembler, linker, libc, libc++, etc.
sudo apt install openmpi-bin openmpi-common libopenmpi-dev libgsl-dev libeigen-dev libblas3 libblas-dev
```
On Ubuntu these binary packages suffice for my purpose. It should be fairly straightforward to build them from source but you have to ensure the `lib` and `include` path are set up correctly. 

## Installing LAMMPS
I performed the procedure on LAMMPS release 29Oct2020. There has been a rename of many `USER-*` packages since, so update the commands accordingly if you use a later version.
 - Download lammps from the releases tarball. Do not use the development repo: LAMMPS do not have CI/CD and the repo is often broken. 
 - `cd <LAMMPS-root>/src`
 - `make ps` gives you package status
 - `make yes-USER-REAXC` installs ReaxFF package
 - `make yes-MISC yes-USER-MISC` installs some 'advanced' commands
 - `make mpi` builds mpi version. 
 
## Shared library support
LAMMPS can be scripted externally. For this to work you need to build it as a shared library. Use `make mode=shared` to do this. See the [manual](https://docs.lammps.org/Build_basics.html) for details. Note that if you link N2P2, you will need to build N2P2 as shared objects as well, and ensure they are discoverable at compile-time to the linker and run-time to the loader. 

## NNP support
Please see [documentation](https://compphysvienna.github.io/n2p2/interfaces/if_lammps.html?highlight=dynamic) for step by step instruction. The automatic build toolchain works well. You can simply issue `make lammps-nnp` and the appropriate LAMMPS version will be downloaded. Then, go into `<path-to-n2p2>/src/interface/LAMMPS/src/`, install any additional packages you want (`make yes-<PACKAGE>`), and build as before.

To support shared library, append `MODE=shared` to the `make` commands. Check that `libnnpif.so` and `libnnp.so` are under `<path-to-n2p2>/lib`. If they do not get built, do `make clean-libnnp clean-libnnpif` under `src/`. Do not forget to `export LD_LIBRARY_PATH=<path-to-n2p2>/lib:${LD_LIBRARY_PATH}`. 

Then go back to `<LAMMPS-root>/src` and make as before. There was a problem with linker not picking up symbols defined in `libnnp` and `libnnpif`. If this happens, go to the relevant makefile and add `-lnnpif -lnnp` to the $(EXTRA_LIB) flag. For instance, my `<LAMMPS-root>/src/MAKE/Makefile.mpi` look like this on line 77:
```
EXTRA_LIB = $(PKG_LIB) $(MPI_LIB) $(FFT_LIB) $(JPG_LIB) $(PKG_SYSLIB) -lnnpif -lnnp
```
# Python support
LAMMPS [documentation](https://docs.lammps.org/Python_install.html) says use `make install-python` will automatically install it for you. If you use conda, be careful that this command tries to put the package into your system python and could mess up your virtual environment. I had my conda environments activated and `make` installed lammps python module to my virtual environment `site-packages` folder using the `pip` from my base environment. To avoid this, read a few more lines of the doc and use `python install.py -p <python package> -l <shared library> [-n]`. 

## ASE integration
ASE has [LAMMPSlib and LAMMPSrun](https://compphysvienna.github.io/n2p2/interfaces/if_lammps.html?highlight=dynamic). I have found LAMMPSlib to work well enough once you get over the headaches of compiling a shared object. The following is an example script using ReaxFF:
```python
from ase.calculators.lammpslib import LAMMPSlib
from ase.io import read

lmp_cmds = ['pair_style reax/c NULL',
            'pair_coeff * * ffield.reax Cu O',
            'fix 1 all qeq/reax 1 0.0 10.0 1e-6 reax/c',
            'neighbor        2 bin',
            'neigh_modify    every 10 delay 0 check no',
            'dump 1 all atom 1 dump.test']

calc = LAMMPSlib(lmpcmds = lmp_cmds,
                 atom_types = {'Cu': 1, 'O': 2},
                 atom_type_masses = {'Cu': 63.546, 'O': 8.0},
                 log_file = 'log-ase.lammps',
                 lammps_header = ['units real',
                                  'atom_style charge',
                                  'atom_modify map yes'])

atoms = read('relaxed.traj')
atoms.calc = calc
en = atoms.get_potential_energy()
```
There is one catch: `atom_modify map yes` is necessary to ensure correct positions are mapped from `ase.Atoms` object to LAMMPS. See discussion [here](https://matsci.org/t/python-interface-to-lammps-scatter-atoms-wont-work-as-expected/32209/2).

## Parallel calculation from python
To use parallel calculation, you need a python interface to MPI (mpi4py). 
```python
from mpi4py import MPI
```
MPI will be initialized upon import. You need to use the same MPI as that used to build LAMMPS itself. In a conda environment, however, when you try to install mpi4py, conda will also install its own MPI which will shadow the system path, causing mpi4py to be compiled against conda's MPI, leading to problems. To avoid this, use pip to install mpi4py and specify source installation only:
```bash
python3 -m pip install --no-binary :all: mpi4py
```

## Getting floating-point types correctly marshalled
As of ASE v3.23 the LAMMPSLib interface does not read forces, velocities, and positions correctly out of the box. The underlying reason is incompatible data type marshalling between LAMMPS's C API and its python bindings. `src/library.h` defines `LAMMPS_INT_DOUBLE = 2` but `lammps.gather_atoms` checks for `type == 1` for doubles, and so LAMMPSLib passes in `type = 1` when calling `gather_atoms` and `scatter_atoms`. Once this type mismatch is fixed, `double` arrays are read in correctly. This however requires a hack to both LAMMPS itself and ASE. 

## Eliminating segfault when used in optimization
Again, as of ASE v3.23 the interface cannot be used in optimizations, leading to [segmentation faults](https://gitlab.com/ase/ase/-/issues/594). This is caused by premature deletion of the `lammps` object, leading to dangling pointers (see my comment in the issue referred). A workaround is setting `keep_alive = True`, although I would expect the interface to fail more gracefully or at least give a comprehensible error message. 
