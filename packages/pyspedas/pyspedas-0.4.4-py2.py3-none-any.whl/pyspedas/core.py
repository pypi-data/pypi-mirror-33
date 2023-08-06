# -*- coding: utf-8 -*-
"""
file: core.py

Desrciption:  
    main function for pyspedas

Example:
    d = pyspedas.load_data('themis', '2015-12-31', ['tha'], '*', 'l2', False)
    
Parameters:
    mission = 'themis': the name of the mission, currently only 'themis' is available
    dates = '2015-12-31': list of dates to be downloaded
    probes = ['tha', 'tha']: list of probes, wildcard ('*') for all probes
    instruments = ['fft']: list of instruments, wildcard ('*') for all instruments
    level = 'l2': either 'l2' or 'l1'
    downloadonly = True: if True then CDF files are downloaded only, if False then they are also loaded into pytplot using pytplot.cdf_to_tplot

List of possible values for L2 themis "instruments" variable:
['efi', 'esa', 'fbk', 'fft', 'fgm', 'fit', 'gmom', 'mom', 'scm', 'sst']

List of possible values for L1 themis "instruments" variable:
['bau', 'eff', 'efp', 'efw', 'esa', 'fbk', 'fff_16', 'fff_32', 'fff_64', 'ffp_16', 'ffp_32', 'ffp_64', 'ffw_16', 'ffw_32', 'ffw_64', 'fgm', 'fit', 'hsk', 'mom', 'scf', 'scm', 'scmode', 'scp', 'scw', 'spin', 'sst', 'state', 'trg', 'vaf', 'vap', 'vaw']

List of possible values for L1 themis "probes" variable:
['tha', 'tha', 'thc', 'thd', 'the']
"""


def load_data(mission, dates, probes, instruments, level, downloadonly):
    """Loads data from mission into pytplot"""    
    
    if mission == 'themis':
        import spd_themis
        spd_themis.load_themis(dates, probes, instruments, level, downloadonly)
    else:
        print("Currently, only themis mission is implemented.")
    
    return 1

def spd_version(): 
    import os.path
    dir_path = os.path.abspath(os.path.dirname(__file__))
    fname = os.path.join(dir_path, 'spd_prefs_txt.py')
    print("Preferences file: " + fname )     
    
    import pkg_resources
    ver = pkg_resources.get_distribution("pyspedas").version
    print("pyspedas version: " + ver)   
