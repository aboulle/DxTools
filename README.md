# DxTools
Processing XRD data files recorded with the Bruker D8 diffractometer

## Supported file formats
For the moment, DxTools suppports Bruker's uxd and brml file formats.
## Features
DxTools automates data formating for most major laboratory XRD experiments:
- Reciprocal space maps: in the (Qx,Qz) plane recorded with the 1D Lynxeye detector,
or recorded with a series of 2theta/theta scans with varying offset;
in the (Qx,Qy) plane recorded with a series of rocking-curves/omega-scans at varying phi angles.

- Temperature experiments: any angular scan vs. temperature.

- X(Y) scan: any angular scan vs. a translation in X or Y.

- Sin^2 psi: recorded either in the conventional chi/psi-tilting geometry or using the variable_incidence (fixed-inclination) method.

- Pole figure: recorded with open detector while rotating chi and phi.

- Custom: any angular/translation scan looped over any other motor or temperature.

## Export options
Depending on the type of experiment, several data exporting options are available.
** No transformation is brought to the data. The raw data is rearranged in various formats.**

- individual scans: all scans are exported with the looping motor name appended to the file name.

- matrix: when the data is 2D, it can be exported in matrix form. First column/row represent the primary and secondary scanning axes.

- 3 columns: when the data is 2D it can also be present in a 3 column format with columns 1 and 2 being the primary and secondary scanning axes.

## Data analysis
When relevant, the peak position, width and area are plotted vs. the secondary scanning axis.
This can be done in 2 ways:
- simple numerical estimation from the data
- automatic fitting with pseudo-Voigt + linear-background function.

Note that is only relevant when there is only one single peak in the scanned area.



