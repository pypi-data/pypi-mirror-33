# README
This is a repository for the CABSdock standalone application for molecular docking of peptides to proteins.
CABSdock allows for flexible docking (also with large-scale conformational changes) without knowledge about the binding site.
CABSdock enables peptide docking using only information about the peptide sequence and the protein receptor structure.
Many advanced options are available that allow for manipulation of a simulation setup, the degree of protein flexibility or guiding the peptide binding etc.
### Detailed instructions and tutorials are provided on [CABSdock WIKI PAGE](https://bitbucket.org/lcbio/cabsdock/wiki)

---

### CABSdock can be installed on Linux, macOS or Windows. To install follow these steps:

### 1. Install *Python2.7*

##### Linux
Most Linux distributions come with *Python2.7* already installed. To check if you have the correct Python version open the terminal and type:

```bash
python --version
```

##### macOS
macOS comes with *Python2.7* already installed. To check if you have the correct Python version open the `Terminal.app` and type:

```bash
python --version
```

If you get the message: `bash: python: command not found` it may mean that your system doesn't have Python installed, or
Python's binary is not in the system `PATH`. To check this run in the `Terminal.app` the following command:

```bash
/Library/Frameworks/Python.framework/Versions/2.7/bin/python --version
```

If you still get the message: `bash: python: command not found` you need to install *Python2.7*. Otherwise add Python's
binary to the system's `PATH` by running in the `Terminal.app` the following command:

```bash
echo "export PATH=/Library/Frameworks/Python.framework/Versions/2.7/bin/:$PATH" >> ~/.bash_profile
```

##### Windows
Follow instructions on [python.org](https://python.org). To check if you have the correct Python version open `command
prompt` (press `cmd + R`; enter "cmd"; hit `enter`) and run the following command:

```commandline
python --version
```

If you get the message: `python: command not found`  add Python's binary to the system's `PATH` by running in the
`command prompt` the following command:

```commandline
set %PATH% = %PATH%;"C:\\path\\to\\python\\binary"
```

Minimum required python version for CABSdock is 2.7.12. You can always download latest version from
[python.org](https://python.org). Note that *Python3.X* is **NOT** the latest version of *Python2.7* and you should
always use *Python2.7* to run CABSdock.

###2. Install pip

##### Linux / macOS / Windows

Assuming you've already installed *Python2.7* and made it accessible under command "python", download
[this](https://bootstrap.pypa.io/get-pip.py) script, change to the directory with downloaded script and run:

```commandline
python get-pip.py
``` 

###3. Install CABS

##### Linux / macOS / Windows

Download latest CABS package from [https://bitbucket.org/lcbio/cabsdock/downloads](https://bitbucket.org/lcbio/cabsdock/downloads/)
and run:

```commandline
pip install CABS<version>.tar.gz
```

If you get an **error** during installation of the matplotlib regarding missing ***libpng*** and/or ***libfreetype*** libraries
you need to install them prior to installing CABS. These should normally be already present on your system. 

###4. Install gfortran

Follow instructions on [gfortran.com](https://www.gfortran.com) 

###5. Install MODELLER (optional)
Follow [instructions](https://salilab.org/modeller/download_installation.html). Remeber to add 
`/modeller/installation/directory/modlib` to PYTHONPATH system variable.


### CABSdock uses some external software packages for the following tasks:

* [gfortran](https://gcc.gnu.org/wiki/GFortran) - Fortran compiler for the CABS core simulations subroutines.
* [MODELLER](https://salilab.org/modeller/) - program for modeling of protein structure using spatial restraints.
CABSdock uses MODELLER for the reconstruction of predicted complexes from tha C-alpha to all-atom representation.
* [libpng](http://www.libpng.org) - library for the png bitmaps.
* [libfreetype](https://www.freetype.org/) - library for the freetype fonts.

---

# ABOUT THE METHOD

CABSdock method has been first made available as a web [server](http://biocomp.chem.uw.edu.pl/CABSdock).
The standalone application version [submitted to publication] provides the same modeling methodology equipped with many
additional features and customizable options.

### The following papers describe the CABS-dock method/ web server/ and its example applications:

* [CABS-dock web server for flexible docking of peptides to proteins without prior knowledge of the binding site,
Nucleic Acids Research, 43(W1): W419-W424, 2015](https://academic.oup.com/nar/article-lookup/doi/10.1093/nar/gkv456)
* [Modeling of protein-peptide interactions using the CABS-dock web server for binding site search and flexible
docking, Methods, 93, 72-83, 2016](http://www.sciencedirect.com/science/article/pii/S1046202315300207)
* [Protein-peptide molecular docking with large-scale conformational changes: the p53-MDM2 interaction, Scientific
Reports 6, 37532, 2016](https://www.nature.com/articles/srep37532)
* [Highly flexible protein-peptide docking using CABS-dock, Methods in Molecular Biology, 1561: 69-94, 2017](
https://link.springer.com/protocol/10.1007%2F978-1-4939-6798-8_6)

### CABS-dock pipeline consist of the three following modules:

* Simulation module – performs docking simulations using peptide sequence, protein structure and set of parameters as
the input. With default settings the module outputs a set of 10’000 of models (10 trajectories consisting of 1000
models) in C-alpha representation.
* Scoring module – selects representative and best-scored models from the simulation module output. Scoring module
outputs sets of 10, 100 and 1000 top-scored models in C-alpha representation.
* Reconstruction to all-atom representation module – uses a Modeller package to reconstruct a set of 10 top-scored
models from C-alpha to all-atom representation.

---

Laboratory of Computational Biology, 2017