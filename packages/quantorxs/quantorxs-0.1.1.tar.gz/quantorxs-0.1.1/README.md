﻿# QUANTORXS : QUANTification of ORganics by X-ray Spectrosocopy

QUANTORXS is an open-source program to automatically analyze XANES spectra at Carbon, Nitrogen and Oxygen K-edges edges to quantify the concentration of functional groups and the elemental ratios (N/C and O/C). It is based on a novel quantification method published in [Analytical chemistry](https://pubs.acs.org/doi/full/10.1021/acs.analchem.8b00689).

QUANTORXS performs the following tasks automatically:

* Load the data from the file(s)
* Remove background
* Normalize the spectra
* Generate a model of the fine structure a fit it to the experimental data
* Calculate the functional groups abundances and elemental rations from the results of the fit
* Generate an Excel file and multiple figures with the results and normalised spectra files.

This is illustrated in more detail in the following diagram:

![Alt text](https://github.com/CorentinLG/QuantORXS/raw/master/Images/Program_sequence.jpg "Sequence of operations performed by the program")

QUANTORXS is designed to work without any user input other than the experimental spectra. Users willing to modify the details of the quantification can download the code from its [GitHub repository](https://github.com/CorentinLG/QuantORXS).

The code was initially written by [Corentin Le Guillou](http://umet.univ-lille1.fr/detailscomplets.php?id=505&lang=fr). [Francisco de la Peña](http://umet.univ-lille1.fr/detailscomplets.php?id=614&lang=fr) created the command line and graphical user interfaces.

## Installing QUANTORXS.

QUANTORXS is written in the Python programming languague and is available from [pypi](https://pypi.org/project/quantorxs). It runs in any operating system with the Python programming language installed.

To install QUANTORXS execute the following in a terminal:

```bash
pip install quantorxs
```

### Step-by-step installation instructions for Windows users

If you are new to Python we reccomend you to install the opensource and free [Anaconda Python distribution](https://www.anaconda.com/download/) for your platform first. Afterwards, from the Microsoft Windows ``Start Menu``, open "anaconda prompt" as in the image below:

![Alt text](https://github.com/CorentinLG/QuantORXS/raw/master/Images/Anaconda_prompt.jpg "where to find anaconda prompt")

Then  type the following and press ``Enter`` (requires connection to the internet):

```bash
pip install quantorxs
```

![Alt text](https://github.com/CorentinLG/QuantORXS/raw/master/Images/Install_command_line.jpg "The install command line")

That's all! QUANTORXS should now be installed in your system.


## Starting the QUANTORXS Graphical User Interface

To start the graphical interface execute the ``quantorxs_gui`` e.g. a terminal. Alternatively, Windows users can start it by  searching for the executable file “quantorxs_gui” in the ``Start Menu`` and launching it as shown in the image below.

![Alt text](https://github.com/CorentinLG/QuantORXS/raw/master/Images/Start_quantorxs.jpg "where to find quantorxs")



## How to use the graphical interface

The program is designed to process several spectra at once. All source spectra should be assembled in one folder.
QUANTORXS reads only the format produced by [aXis2000](http://unicorn.mcmaster.ca/aXis2000.html)

* Click on the ``Choose data directory`` button and select the folder containing the source spectra.
* Type in an output folder name (relative to the data directory) to store the results of the analysis. The default is ``QUANTORXS results``.
* Make sure that the ``demo`` box is not checked. If checked, it uses default files as input to produce an example of the output files.
* Select the format of the figure output (the default is SVG)
* Set the ``offset`` if required to compensate from any energy misalignment (e.g. from poorly calibrated monochromator) *common to all spectra*.
* Click the ``Run`` button and wait until the analysis is completed (usually a few secondes per spectrum).

![Alt text](https://github.com/CorentinLG/QuantORXS/raw/master/Images/Quantorxs_gui.jpg "The graphical user interface")

## Description of the output files

The output folder will be created in the folder from which the data have been taken.
An .xls result file and two different sub-folders are created:

### a .xls file contains several sheets:
* The fitting parameters
* The quantified data (aromatic, ketones, aliphatics, carboxylics; as well as N/C and O/C ratios) and some related plots
* The spectra at the C-K edge normalized by the area ratio method
* The spectra at the N-K edge normalized by the area ratio method
* The spectra at the O-K edge normalized by the area ratio method
* The fitted heights of the Gaussians for the area-based normalization at the C-K edge
* The fitted heights of the Gaussians for the area-based normalization at the N-K edge
* The fitted heights of the Gaussians for the area-based normalization at the O-K edge

![Alt text](https://github.com/CorentinLG/QuantORXS/raw/master/Images/excel_Tab1.jpg "Analysis parameters")

![Alt text](https://github.com/CorentinLG/QuantORXS/raw/master/Images/excel_Tab2.jpg "Quantified data")

![Alt text](https://github.com/CorentinLG/QuantORXS/raw/master/Images/excel_Tab3.jpg "normalized spectra")

![Alt text](https://github.com/CorentinLG/QuantORXS/raw/master/Images/excel_Tab4.jpg "fitted gaussians")

### A folder containing the .txt files of each normalized spectrum

### A folder with figures displaying:

* The cross-section fit
* The normalized spectra
* The deconvolution (all gaussians included)
