# -*- coding: utf-8 -*-
"""
file: load_data.py

Desrciption:  
    Main function for pyspedas

Example:
    pyspedas.load_data('themis', '2015-12-31', ['tha'], '*', 'l2', False)
    
Parameters:
    mission: str/list of str
        The name of the mission (eg. 'themis')
    dates: str/list of str ['yyyy-mm-dd']
        List of dates to be downloaded (eg. ['2015-12-31'])
    probes: str/list of str
        Probes for missions with multiple probes (eg. ['tha', 'thb']), wildcard ('*') for all probes
    instruments: str/list of str
        List of instruments (eg. ['fft']), wildcard ('*') for all instruments
    level: str
        Usually, either 'l2' or 'l1', depends on mission
    downloadonly: bool (True/False)
        If True then CDF files are downloaded only, if False then they are also loaded into pytplot using pytplot.cdf_to_tplot
    varformat : str
        The file variable formats to load into tplot.  Wildcard character 
            "*" is accepted.  By default, all variables are loaded in.  
    get_support_data: bool
        Data with an attribute "VAR_TYPE" with a value of "support_data"
            will be loaded into tplot.  By default, only loads in data with a 
            "VAR_TYPE" attribute of "data".
    prefix: str
        The tplot variable names will be given this prefix.  By default, no prefix is added.
    suffix: str
        The tplot variable names will be given this suffix.  By default, no suffix is added.
"""


def load_data(mission, dates, probes, instruments, level, downloadonly=False, varformat=None, get_support_data=False, prefix='', suffix=''):
    """Loads data from mission into pytplot"""    
    
    if mission == 'themis':
        from pyspedas import themis_load
        themis_load(dates, probes, instruments, level, downloadonly, varformat, get_support_data, prefix, suffix)
    if mission == 'omni':
        from pyspedas import omni_load
        #level = 1m, 5m
        omni_load(dates, level, downloadonly, varformat, get_support_data, prefix, suffix)
    else:
        print("Currently, only the THEMIS and OMNI missions are implemented.")    
    
    print('Data loading finished.')

 
