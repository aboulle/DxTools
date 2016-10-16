# DxTools
Processing XRD data files recorded with the Bruker D8 diffractometer

## Installation instructions
DxTools requires  [python 3] (http://www.python.org), [SciPy](http://www.scipy.org), [Matplotlib](http://www.matplotlib.org).
DxTools is not compatible with Python 2.7 and below.

### Linux
In a terminal run (as root) `apt install python3 python3-scipy python3-matplolib`.
Run DxTools with `python3 dxtools.py`

### MS Windows
If you have a python 2.7 installation that you want to keep, you will need to have a separate installation of python 3.
A simple way to manage different Python environments is to use the  [Anaconda](http://continuum.io/downloads) distribution.
After installation, in a command window create a Python 2.7 environment with
`conda create -n py27 python=2.7 anaconda`
and a Python 3.5 environment with `conda create -n py35 python=3.5 anaconda`.
Switch from one to another with `activate py27` and `activate py35`.
Anaconda includes all dependences needed for DxTools.
Run DxTools with `python dxtools.py`



## Features
DxTools automates data formating for most major laboratory XRD experiments:
- Reciprocal space maps: in the (Qx,Qz) plane recorded with a 1D detector,
or recorded with a series of 2theta/theta scans with varying offset;
in the (Qx,Qy) plane recorded with a series of rocking-curves/omega-scans at varying phi angles.

- Temperature experiments: any angular scan vs. temperature.

- X(Y) scan: any angular scan vs. a translation in X or Y.

- Sin^2 psi: recorded either in the conventional chi/psi-tilting geometry or using the variable-incidence (fixed-inclination) method.

- Pole figure: recorded with open detector while rotating chi and phi.

- Custom: any angular/translation scan looped over any other motor or temperature.

### Export options
Depending on the type of experiment, several data exporting options are available.
** No transformation is brought to the data. The raw data is rearranged in various formats.**

- individual scans: all scans are exported with the looping motor names appended to the file name.

- matrix: when the data is 2D, it can be exported in matrix form. First column/row represent the primary and secondary scanning axes.

- 3 columns: when the data is 2D it can also be present in a 3 column format with columns 1 and 2 being the primary and secondary scanning axes.

### Data analysis
When relevant, the peak position, width and area are plotted vs. the secondary scanning axis.
This can be done in 2 ways:
- simple numerical estimation from the data
- automatic fitting with a pseudo-Voigt (+ linear-background) function.

Note that is only relevant when there is one single peak in the scanned area.

### Point skipping
The data range can be cropped for the primary and secondary scanning axes by specifying the number of data points to be removed at the beginning and the end of the scanning range.
This is useful to eliminate artifacts at the edges of the 1D detector or reduce an otherwise excessive scanning range.

### Supported file formats
For the moment, DxTools suppports Bruker's uxd and brml file formats.



