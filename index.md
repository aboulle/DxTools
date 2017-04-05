## Installation instructions
DxTools requires [Python 3](http://www.python.org), [SciPy](http://www.scipy.org) and [Matplotlib](http://www.matplotlib.org).
DxTools is not compatible with Python 2.7 and below.

### Linux
In a terminal run (as root) `apt install python3 python3-scipy python3-matplolib`.
In the DxTools folder, run the program with `python3 dxtools.py`

### MS Windows
The most straightforward way to install Python and all required dependencies in Windows is to install 
a full-featured scientific Python distribution, like [Anaconda](http://continuum.io/downloads), [Canopy](https://www.enthought.com/products/canopy/),
or [Python(x,y)](https://python-xy.github.io/).


If you have a Python 2.7 installation that you want to keep, you will need to have a separate installation of Python 3.
A simple way to manage different Python environments is to use the  [Anaconda](http://continuum.io/downloads) distribution.
After installation, in a command window create a Python 2.7 environment with
`conda create -n py27 python=2.7 anaconda`
and a Python 3.5 environment with `conda create -n py35 python=3.5 anaconda`.
Switch from one to another with `activate py27` and `activate py35`.

## Usage
Download DxTools and uncompress the archive to your hard drive.
In a command-line window, move to the DxTools folder and run the program with `python dxtools.py` (Windows) or `python3 dxtools.py` (Linux).
The typical workflow with DxTools is the following:
- Open data from the "File" menu (uxd or brml format)
- Select the experiment type from the tab bar (see below)
- Select data processing and data analysis options (see below)
- Process data

The processed data files are automatically saved to your hard drive in the same folder as the input data.
The figures can be saved from the interface. While processing, a temporary tmp file (containg all raw data) is written in the DxTools folder.
It is automatically deleted upon closing.

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
*No modification is brought to the intensity values. The raw data is only rearranged in various formats.*

- individual scans: all scans are exported with the looping motor names appended to the file name.
- matrix: when the data is 2D, it can be exported in matrix form. First column/row represent the primary and secondary scanning axes.
- 3 columns: when the data is 2D it can also be presented in a 3 column format with columns 1 and 2 being the primary and secondary scanning axes.

### Data analysis
When relevant, the peak position, width and area are plotted vs. the secondary scanning axis.
This can be done in 2 ways:
- simple numerical estimation from the data
- automatic fitting with a pseudo-Voigt (+ linear-background) function.

Note that is only relevant when there is one single peak in the scanned area.

### Point skipping
The data range can be cropped along the primary and secondary scanning axes by specifying the number of data points to be removed at the beginning and the end of the scanning ranges.
This is useful to eliminate artifacts at the edges of the 1D detector or reduce an otherwise excessive scanning range.

### Supported file formats
For the moment, DxTools suppports Bruker's uxd and brml file formats.



