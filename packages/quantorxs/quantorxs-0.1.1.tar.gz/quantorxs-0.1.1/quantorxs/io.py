import numpy as np
import pkg_resources


### open the F2 files and fills arrays with their values.
def openf2 (source_file):
    path = pkg_resources.resource_filename("quantorxs", source_file)
    E_f2, OD_f1, OD_f2 =  np.loadtxt(path, comments='#').T
    return E_f2, OD_f2

#Open and reads the spectra from the directory
def openfile(spectrum_path):
    E, OD = np.loadtxt(spectrum_path, comments="%").T
    return E, OD
