# -*- coding: utf-8 -*-
"""
Created on Tue Jun 26 10:35:42 2018

adds -d

@author: nikos
"""
import pyspedas
import pytplot
import numpy

def substract_average(names, new_names=None):
    old_names = pyspedas.tnames(names)
    if len(old_names) < 1:
        print('Subtract Average error: No tplot variables given.')
        return 
    
    if new_names == None:
        n_names = names
    elif new_names == '*':
        n_names = [s + '-d' for s in names]
    else:
        n_names = new_names
    
    if len(n_names) != len(old_names):
        print('Subtract Average error: Length of new names list is not the same as length of existing names.')
    
    for i in range(len(old_names)):
        time, data = pytplot.get_data(old_names[i])         
        pytplot.store_data(n_names[i], data={'x':time, 'y':data-numpy.mean(data)})
        print('Subtract Average applied to '+ n_names[i])
        
        
    