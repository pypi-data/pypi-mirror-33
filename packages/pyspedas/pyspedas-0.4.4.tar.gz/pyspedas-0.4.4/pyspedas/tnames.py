# -*- coding: utf-8 -*-
"""
file: tnames.py

Desrciption:  
    Finds all tplot names that follow a pattern that contains a wildcard
    Wildcards: ? for a single character, * from multiple characters
    
Returns:
    A list of tplot names
"""

import pytplot
import fnmatch

def tnames(pattern=None):
    all_names = pytplot.tplot_names()
    if pattern==None:
        return all_names
    else:
        filtered = fnmatch.filter(all_names, pattern)
        return filtered 