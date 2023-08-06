# -*- coding: utf-8 -*-
"""
file: omni_load.py

Desrciption:  
    Data loading functions for OMNI  
    
Example:
    d = pyspedas.omni_load('2015-12-31', '5min', False)
    
Parameters:
    dates: list of strings ['yyyy-mm-dd'], list of dates to be downloaded (eg. ['2015-12-31'])
    level: string, either '1min' or '5min' 
    downloadonly: True/False, if True then CDF files are downloaded only, if False then they are also loaded into pytplot using pytplot.cdf_to_tplot
    suffix: string, a string suffix to be added to pytplot variables

"""

import os
import pytplot
import pyspedas 

def omni_filename(dates, level):
    """Create a list of tuples for downloading: remote_file, local_file"""
    prefs = pyspedas.get_spedas_prefs()
    if 'omni_remote' in prefs: 
        #https://cdaweb.gsfc.nasa.gov/istp_public/data/omni/hro_1min/2017/
        remote_path = prefs['omni_remote']
    else:
        raise NameError('remote_path is not found in spd_prefs.txt')
    if 'data_dir' in prefs: 
        data_dir = prefs['data_dir'] + 'omni'
        
    else:
        raise NameError('data_dir is not found in spd_prefs.txt')

    if level!='1min':
        level = '5min'    
        
    dates = pyspedas.get_dates(dates)
    version = '?'
    
    file_list = []
    for sdate in dates:
        year = sdate[0:4]
        month = sdate[5:7]
        day = sdate[8:10]
        
        # file_dir = 'hro_1min/2017/'
        file_dir = 'hro_' + level + '/' + year 
        file_dir_local = os.path.join('hro_', level, year)
        # filename = 'omni_hro_1min_20171201_v01.cdf'
        filename = 'omni_hro_' + level + '_' + year + month + '01' + '_v0' + version + '.cdf'
        
        remote_file = remote_path + '/' + file_dir  + '/' + filename
        local_file = os.path.join(data_dir, file_dir_local, filename)
        
        file_list.append((remote_file, local_file))                

    return file_list


def omni_load(dates, level, downloadonly, suffix=''):
    """Loads themis data into pytplot variables"""
    
    file_list = omni_filename(dates, level)
    
    count = 0
    dcount = 0
    for remotef, localf in file_list:   
        count += 1
        resp, err, locafile = pyspedas.download_files(remotef, localf)
        if resp:
            print(str(count) + '. File was downloaded. Location: ' + locafile)
            dcount += 1
            if not downloadonly:
                try: 
                    testcdf = pytplot.cdf_to_tplot(locafile, suffix)                
                    print(testcdf) 
                except TypeError as e:
                    msg = "cdf_to_tplot could not load " + locafile + "\nError:\n" + str(e)
                    print(msg)
            
        else:
            print(str(count) + '. There was a problem. Could not download file: ' + remotef)
            print(err)        

    print('Downloaded ' + str(dcount) + ' files.')
    print('tplot variables:')
    print(pytplot.tplot_names())