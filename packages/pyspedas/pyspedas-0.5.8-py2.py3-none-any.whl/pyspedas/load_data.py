# -*- coding: utf-8 -*-
"""
file: load_data.py

Desrciption:  
    Main function for pyspedas

Example:
    d = pyspedas.load_data('themis', '2015-12-31', ['tha'], '*', 'l2', False)
    
Parameters:
    mission: string, the name of the mission (eg. 'themis')
    dates: list of strings ['yyyy-mm-dd'], list of dates to be downloaded (eg. ['2015-12-31'])
    probes: list of strings, probes (eg. ['tha', 'thb']), wildcard ('*') for all probes
    instruments: list of strings, list of instruments (eg. ['fft']), wildcard ('*') for all instruments
    level: string, either 'l2' or 'l1', depends on mission
    downloadonly: True/False, if True then CDF files are downloaded only, if False then they are also loaded into pytplot using pytplot.cdf_to_tplot
    suffix: string, a string suffix to be added to pytplot variables
"""


def load_data(mission, dates, probes, instruments, level, downloadonly, suffix):
    """Loads data from mission into pytplot"""    
    
    if mission == 'themis':
        from pyspedas import themis_load
        themis_load(dates, probes, instruments, level, downloadonly, suffix)
    if mission == 'omni':
        from pyspedas import omni_load
        #level = 1m, 5m
        omni_load(dates, level, downloadonly, suffix)
    else:
        print("Currently, only the THEMIS and OMNI missions are implemented.")    
    return 1

 
