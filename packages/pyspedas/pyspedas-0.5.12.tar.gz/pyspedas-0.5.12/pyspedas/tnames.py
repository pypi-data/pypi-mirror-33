# -*- coding: utf-8 -*-
"""
file: tnames.py

Desrciption:  
    Finds all tplot names that follow a pattern that may contain a wildcard
    
Parameters:
    pattern: str/list of str ['yyyy-mm-dd']
        List of string patterns

Notes:
    Allowed wildcards are ? for a single character, * from multiple characters
    
Returns:
    A list of tplot names
"""

import pytplot
import fnmatch

def tnames(pattern=None):
    
    name_list = list()
    all_names = pytplot.tplot_names()
    
    if pattern==None:
        name_list.extend(all_names)
    else:
        if isinstance(pattern, str):
            name_list.extend(fnmatch.filter(all_names, pattern))
        else:
            for p in pattern: 
                name_list.extend(fnmatch.filter(all_names, p))
    
    return name_list 