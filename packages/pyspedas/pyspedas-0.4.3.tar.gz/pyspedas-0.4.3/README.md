# pyspedas

Load data from SPEDAS CDF files into pytplot. 

Pyspedas is a python package that contains data loading modules for various scientific NASA missions. 

The load routines are designed to work with the libraries [cdflib](https://github.com/MAVENSDC/cdflib), [pytplot](https://github.com/MAVENSDC/PyTplot).

### How It Works

CDF files are downloaded from the internet to the local machine. 
The data from these files is loaded into pytplot objects and these objects can be plotted. 

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Install Python

Python 3.5+ is required.  

We recommend [Anaconda](https://www.continuum.io/downloads/) which comes with a suite of packages useful for science. 

### Install pyspedas

To install pyspedas, open a command line and use the command:

`pip install pyspedas`

### Upgrade pyspedas

If you have already installed pyspedas, to upgrade to the latest version use the command:

`pip install pyspedas --upgrade`


## Running pyspedas

After installation, please change the file `pyspedas/prefs.ini` and set `data_dir=C:\Datapy\themis` to a directory of your choice. This is the local directory where the CDF files will be saved. 

To download CDF files for the Themis mission, use: 

`pyspedas.load_data(mission, dates, probes, instruments, level, downloadonly)`

For example: 

`d = pyspedas.load_data('themis', '2015-12-31', ['tha'], 'state', 'l1', False)`

### Crib sheets

Folder `tests` contains some crib sheets to get you started. 

### THEMIS variables

List of possible values for the "probes" variable:

`['tha', 'thb', 'thc', 'thd', 'the']`

List of possible values for the L2 "instruments" variable:

`['efi', 'esa', 'fbk', 'fft', 'fgm', 'fit', 'gmom', 'mom', 'scm', 'sst']`

List of possible values for L1 "instruments" variable:

`['bau', 'eff', 'efp', 'efw', 'esa', 'fbk', 'fff_16', 'fff_32', 'fff_64', 'ffp_16', 'ffp_32', 'ffp_64', 'ffw_16', 'ffw_32', 'ffw_64', 'fgm', 'fit', 'hsk', 'mom', 'scf', 'scm', 'scmode', 'scp', 'scw', 'spin', 'sst', 'state', 'trg', 'vaf', 'vap', 'vaw']`

> **Parameters**:
>  
> - `mission = 'themis'`   the name of the mission, currently only 'themis' is available
> - `dates = '2015-12-31'` list of dates to be downloaded	
> - `probes = ['tha', 'tha']`  list of probes ['tha', 'tha', 'thc', 'thd', 'the'], wildcard ('*') for all probes 
> - `instruments = ['fft']` list of instruments, wildcard ('*') for all instruments  
> - `level = 'l2'`  either 'l2' or 'l1'
> - `downloadonly = True` if True then CDF files are downloaded only, if False then they are also loaded into pytplot using pytplot.cdf_to_tplot


### Additional Information

For pytplot, see: https://github.com/MAVENSDC/PyTplot

For cdflib, see: https://github.com/MAVENSDC/cdflib

For SPEDAS, see http://spedas.org/blog/

For information on the Themis mission, see http://themis.ssl.berkeley.edu/ 

