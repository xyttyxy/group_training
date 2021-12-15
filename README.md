# Sautet Group - New Student Training
---
## Introduction
This repository records and fascilitates training of new students to the Sautet group which primarily works in computational catalysis. Topics covered include (or will include):
- Basic Linux commands
- Compute clusters and job schedulers
- Compiling parallel programs
- Python and Atomic Simulation Environment (ASE)
- (very) basic solid state physics and DFT
- VASP tutorials and tips

## Cluster access
As beginners you will only need UCLA's own (free) hoffman2 cluter for learning. You can register an account following this:
https://www.hoffman2.idre.ucla.edu/Accounts/Requesting-an-account.html

## Shell access and commands
Shell is basically another word for user interface. Since the vast majority of computing tools is best accessed via command-line interfaces, you will need to become familiar with basic commands. Commands are a way of instructing the computer to perform certain tasks, much like mouse clicks on buttons and filling out forms in the graphical user interface (GUI). Depending on your local operating system (your laptop), you may or may not already have a shell environment ready.
### OS X Setup
Macs come with a bash shell out of the box. No need to do anything.
### Windows Setup
The native shells in Windows (CMD.exe and PowerShell) unfortunately are not compatible with many basic commands and tools we use. So you will need to setup a separate environment. There are a few ways to do this but on modern systems the best way by far is the Windows Subsystem for Linux (WSL) which is a lightweight virtual machine that immediately gives you an Linux environment inside of Windows. Plenty of tutorials exist online for you to follow. Note that as this is rapidly changing piece of software, make sure to follow ones that match your Windows version (which can be found by typing Win+R -> 'winver' -> Enter). A good one is provided by MS themselves:
https://docs.microsoft.com/en-us/windows/wsl/install

You will need to choose a distribution of Linux. A distribution is a collection of software that comes prebundled with the core OS, tailored to different purposes and communities. We recommend either CentOS (used by most supercomputing clusters) or Ubuntu (more user-friendly tools, better availability of help online, good desktop environment). Whichever you choose, the basic commands are the same. 

### Basic Commands
Once you have your local shell ready, you need to familarize yourself with basic file operations and commands. The following tutorial is actually for UNIX but the commands are the same for our concerns. Following the first 2 chapters are enough for now, but eventually you will need to be familiar with most of the stuff there.
https://rc.byu.edu/documentation/unix-tutorial/

### SSH
SSH stands for secure shell and is a way to send commands and receive output over a network. This is the connection protocol (also a command in itself) you will use to connect to clusters. Follow this link to learn the basics of it:
https://www.ccn.ucla.edu/wiki/index.php/Hoffman2:Accessing_the_Cluster

You may want to save yourself the trouble of typing passwords everytime by creating a public key and storing it on the server (cluster):
https://serverpilot.io/docs/how-to-use-ssh-public-key-authentication/

### VASP
[VASP](https://www.vasp.at/) stands for Vienna Ab-initio Simulation Package. It is a very popular package for density functional theory calculations in periodic systems. The VASP [Manual](https://www.vasp.at/wiki/index.php/The_VASP_Manual) has everything you need to know about it. Information on how to compile it on various clusters can be found [here](vasp/vasp.md). 
