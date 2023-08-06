# -*- coding: utf-8 -*-
"""
file: core.py

Desrciption:  
    loading functions for themis

"""

import os
import spd_helpers
import spd_dates
import spd_prefs
import pytplot

def themis_filename(dates, probes, instruments, level):
    """Create a list of tuples for downloading: remote_file, local_file"""
    prefs = spd_prefs.get_spedas_prefs()
    if 'themis_remote' in prefs: 
        remote_path = prefs['themis_remote']
    else:
        raise NameError('remote_path is not found in spd_prefs.txt')
    if 'data_dir' in prefs: 
        data_dir = prefs['data_dir']
        
    else:
        raise NameError('data_dir is not found in spd_prefs.txt')

    if level!='l1':
        level = 'l2'    
    probes = spd_helpers.get_probes(probes)
    instruments = spd_helpers.get_instruments(instruments, level)
    dates = spd_dates.get_dates(dates)

    if level == 'l1':
        version = '?'
    else:
        version = '1'
    
    file_list = []
    for sdate in dates:
        year = sdate[0:4]
        month = sdate[5:7]
        day = sdate[8:10]
        for probe in probes:
            for instrument in instruments: 
                # file_dir = 'tha/l2/fgm/2015/'
                file_dir = probe + '/' + level + '/' + instrument + '/' + year
                file_dir_local = os.path.join(probe, level, instrument, year)
                # filename = 'tha_l2_fgm_20150101_v01.cdf'
                filename = probe + '_' + level + '_' + instrument + '_' + year + month + day + '_v0' + version + '.cdf'
                
                remote_file = remote_path + '/' + file_dir  + '/' + filename
                local_file = os.path.join(data_dir, file_dir_local, filename)
                
                file_list.append((remote_file, local_file))
                

    return file_list


def load_themis(dates, probes, instruments, level, downloadonly):
    """Loads themis data into pytplot variables"""
    
    file_list = themis_filename(dates, probes, instruments, level)
    
    count = 0
    dcount = 0
    for remotef, localf in file_list:   
        count += 1
        resp, err, locafile = spd_helpers.download_files(remotef, localf)
        if resp:
            print(str(count) + '. File was downloaded. Location: ' + locafile)
            dcount += 1
            if not downloadonly:
                try: 
                    testcdf = pytplot.cdf_to_tplot(locafile)                
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
