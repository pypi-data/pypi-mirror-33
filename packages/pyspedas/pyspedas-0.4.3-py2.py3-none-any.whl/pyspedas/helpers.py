# -*- coding: utf-8 -*-
"""
file: helpers.py

Desrciption:  
    Helper functions for pyspedas

"""

import urllib
import os

def download_files(url, locafile):
    """Get a file from internet and save it localy."""
    
    exists = False    
    httpreq = None
    err = None
    ver = -1
    
    exists, err, ver, newurl = find_latest_url_version(url)
    if not exists:
        return exists, err, locafile
    
    url = newurl
    if ver != -1:
        locafile = locafile.replace('?', str(ver))
    
    #Create local directory if it does not exist
    dirPath = os.path.dirname(locafile)
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)
    
    # Download file
    try:
        httpreq = urllib.request.urlretrieve(url, locafile)
    except urllib.request.URLError as e:
        httpreq = None
        err = e        
        
    if httpreq is not None:    
        exists = True
  
    return exists, err, locafile

def url_exists(url):
    """Returns True if url exists, otherwise False"""
    
    ans = False
    try:
        urllib.request.urlopen(url)
        ans = True
        err = ''
    except urllib.request.URLError as e:
        ans = False   
        err = e
        
    return ans, err

def find_latest_url_version(url):
    """Returns if a file exists and the latest version.
    Assumes max version = v04, should be changed if there are higher versions
    """
    
    exists = False
    err = ''
    ver = -1
    newurl = url
    if '?' in url:
        for ver in range(4, -1, -1):
            newurl = url.replace('?', str(ver))
            exists, err = url_exists(newurl)
            #print(exists, err, ver, newurl)
            if exists:
                break
    else:
        ver = -1
        newurl = url
        exists, err = url_exists(newurl)
        return exists, err, ver, newurl
    
    return exists, err, ver, newurl


def get_probes(probes):
    """Returns a list of probes"""
    probe_list = ['a', 'b', 'c', 'd', 'e' ]
    thprobe_list = ['tha', 'thb', 'thc', 'thd', 'the' ]
    ans_list = []
    if not isinstance(probes, (list, tuple)):
        probes = [probes]
        
    for p in probes:
        p = p.lower()
        if p=='*':
            ans_list = thprobe_list;
            break; 
        if p in probe_list:
            ans_list.append('th' + p)
        elif p in thprobe_list:  
            ans_list.append(p)  
    
    return ans_list

def get_instruments(instruments, level):
    """Returns a list of themis instruments for L2 data"""
    if level=='l1':
        instr_list = ['bau', 'eff', 'efp', 'efw', 'esa', 'fbk', 'fff_16', 'fff_32', 'fff_64', 'ffp_16', 'ffp_32', 'ffp_64', 'ffw_16', 'ffw_32', 'ffw_64', 'fgm', 'fit', 'hsk', 'mom', 'scf', 'scm', 'scmode', 'scp', 'scw', 'spin', 'sst', 'state', 'trg', 'vaf', 'vap', 'vaw']
    elif level=='l2_mag':
        instr_list = instruments
    else:
        instr_list = ['efi', 'esa', 'fbk', 'fft', 'fgm', 'fit', 'gmom', 'mom', 'scm', 'sst']
    ans_list = []
    if not isinstance(instruments, (list, tuple)):
        instruments = [instruments]
        
    for p in instruments:
        p = p.lower()
        if p=='*':
            ans_list = instr_list;
            break; 
        if p in instr_list:
            ans_list.append(p)
    
    return ans_list
