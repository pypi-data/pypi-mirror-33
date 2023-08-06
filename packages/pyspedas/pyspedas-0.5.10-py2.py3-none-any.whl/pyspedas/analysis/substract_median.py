# -*- coding: utf-8 -*-
"""
file: substract_median.py

Desrciption:  
    Substracts the median from the data.
    Result well be saved in:
        - The same tplot variable names if new_names is not given
        - The new_names list if it has same length as names
        - The name followed by '-d' otherwise
        
    Wildcards in names: ? for a single character, * from multiple characters

"""
import pyspedas
import pytplot
import numpy

def substract_median(names, new_names=None):
    old_names = pyspedas.tnames(names)
    if len(old_names) < 1:
        print('Subtract Average error: No tplot variables given.')
        return 
    
    if new_names == None:
        n_names = names
    elif new_names == '*' or new_names == '':
        n_names = [s + '-d' for s in old_names]
    else:
        n_names = new_names
    
    if len(n_names) != len(old_names):
        n_names = [s + '-d' for s in old_names]
    
    for i in range(len(old_names)):
        time, data = pytplot.get_data(old_names[i])         
        pytplot.store_data(n_names[i], data={'x':time, 'y':data-numpy.median(data)})
        print('Subtract Average applied to '+ n_names[i])
        