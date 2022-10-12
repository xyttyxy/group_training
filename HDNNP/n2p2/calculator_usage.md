# A primitive ASE calculator has been written to launch n2p2 calculation from python. 

*Warning*: this has very poor I/O performance and should not be used for high-throughput calculations (e.g. big/long MD)

- [ase calculator](https://github.com/vsumaria/ASE_N2P2)

## Installation
1. The simplest way to use this is creating a new conda environment, clone the ase fork above, install with pip
```
conda create -n <env_name>
conda activate <env_name>
conda install pip
git clone https://github.com/vsumaria/ASE_N2P2.git
cd ASE_N2P2/ase/ase && pip install .
```
2. Another way is to use the official ASE repo. For this you must use the master development branch, and not the release (3.21.1 as of 09/26/2022). Create the conda environment as before, then do:
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

## Usage
the README.md under the calculator repo has pretty much all you need. Just note that directory is NNP working directory, not the directory where the NNP files are stored. The calculator will copy files over to this directory and launch calculation there. Because the calculator does lots of file and stdout I/O for every prediction, it is not scalable w.r.t. number of structures. You need to specify the relative path to `input.nn`, etc. 
