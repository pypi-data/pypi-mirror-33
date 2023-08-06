# -*- coding: utf-8 -*-
"""
file: subtract_average.py

Desrciption:  
    Subtracts the average from the data.
    
Parameters:
    names: str/list of str  
        List of pytplot names
    new_names: str/list of str
        List of new_names for pytplot variables
    suffix: 
        A suffix to apply. Default is '-m'.
        
Notes:
    Allowed wildcards are ? for a single character, * from multiple characters   

"""
import pyspedas
import pytplot
import numpy
        
def subtract_average(names, new_names=None, suffix=None):
    old_names = pyspedas.tnames(names)
    
    if len(old_names) < 1:
        print('Subtract Median error: No tplot variables provided.')
        return 
    
    if suffix == None:
        suffix = '-m'
    
    if new_names == None:
        n_names = [s + suffix for s in old_names]
    elif new_names == '*' or new_names == '':
        n_names = old_names
    else:
        n_names = new_names
    
    if len(n_names) != len(old_names):
        n_names = [s + suffix for s in old_names]
    
    for i in range(len(old_names)):
        time, data = pytplot.get_data(old_names[i])       
        new_data = data-numpy.mean(data, axis=0)        
        pytplot.store_data(n_names[i], data={'x':time, 'y':new_data})
        print('Subtract Median applied to: '+ n_names[i])        
    