# ASE integration for N2P2
There are 2 ASE calculators AFAIK. The development history is [here](https://github.com/CompPhysVienna/n2p2/issues/142) and [here](https://gitlab.com/ase/ase/-/merge_requests/2581). 

## Vaidish's [file I/O-based calculator](https://github.com/vsumaria/ASE_N2P2) 
*Warning*: this has very poor I/O performance and should not be used for high-throughput calculations (e.g. big/long MD)
### Installation
The simplest way to use this is creating a new conda environment, clone the ase fork above, install with pip
```
conda create -n <env_name>
conda activate <env_name>
conda install pip
git clone https://github.com/vsumaria/ASE_N2P2.git
cd ASE_N2P2/ase/ase && pip install .
```

Another way is to use the official ASE repo. For this you must use the master development branch, and not the release (3.21.1 as of 09/26/2022). Create the conda environment as before, then do:
```
git clone https://gitlab.com/ase/ase.git
cd ase && pip install
```
Then, download the individual files to some local directory
```
mkdir <n2p2_calculator>
curl -o n2p2_io.py https://github.com/vsumaria/ASE_N2P2/blob/main/ase/ase/io/n2p2.py 
curl -o n2p2_calc.py https://raw.githubusercontent.com/vsumaria/ASE_N2P2/main/ase/ase/calculators/n2p2.py
```
change the import statement from
`from ase.io.n2p2 import ...`
to
`from n2p2_io import ...`
in order for python interpreter to find the n2p2\_io and n2p2_calc files, you can use conda-build. 
`conda install -n base conda-build`
`cd <n2p2_calculator>`
`conda develop .`
this will create a `conda.pth` file under `site-packages` directory in your conda environment. Now the calculator scripts can be used from anywhere. 

### Usage
the README.md under the calculator repo has pretty much all you need. Just note that directory is NNP working directory, not the directory where the NNP files are stored. The calculator will copy files over to this directory and launch calculation there. Because the calculator does lots of file and stdout I/O for every prediction, it is not scalable w.r.t. number of structures. You need to specify the relative path to `input.nn`, etc. 

## Mike Water's [PyNNP-based calculator](https://gitlab.com/mjwaters/ase). 
This is with python bindings to the C++ API. I (Yantao) have tested this to be much more scalable/faster. *Recommended.*
However, it is a bit more involved to set up. If you don't care about scalability/efficiency, use the first one.
### Installation
#### Installing the fork
Because this fork is not tested, it is recommended you set up a fresh conda environment to do this. You can copy the packages from your existing environment as:
```sh
conda activate old_env
conda list --explicit > spec_file.txt
conda create --name new_env --file spec_file.txt
conda activate new_env
```
Then, download and install the fork:
```sh
cd ~/Downloads
git clone git clone https://gitlab.com/mjwaters/ase.git
cd ase
python3 -m pip install .
```
This will install the fork if your `old_env` does not have ase installed, and replace the release version with the fork if it does. Check that it works:
```sh
cd
python3 -c 'from ase.calculators.pynnp import PyNNP'
```

#### Installing the pynnp module
```sh
cd <n2p2_root>/src/pynnp
make
```
it should build a shared library, something like pynnp.cpython-310-x86_64-linux-gnu.so. At this point, the normal procedure is to do
```sh
python3 -m pip install .
```
However, there is a problem with the shipped `Setup.py` and/or `pip` and the package ends up getting installed as UNKNOWN. When this happens, use conda's (also broken, but works for our purpose) `conda develop` as a workaround:
```sh
conda activate new_env
conda -n base install conda-build
# while in pynnp folder
conda develop .
```
This should create `$CONDA_PREFIX/lib/python3.*/site-packages/conda.pth` and append `$PWD` to it. Now you can verify you can access pynnp anywhere on the system:
```sh
cd
python3 -c 'import pynnp'
```
