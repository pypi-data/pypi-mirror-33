# -*- coding: utf-8 -*-
"""
File: 
    ex_create.py

Desrciption:  
    Creates a new pytplot object and applies analysis functions.

"""

import pyspedas
import pytplot
import numpy

def ex_create():
    #Create a sin wave plot
    a = list(range(0,101))
    b = [2.0/100.0*numpy.pi*s for s in a]
    c = pyspedas.time_float('2017-01-01')
    x = list()
    y = list()
    for i in range(len(b)):
        x.append(c+60.0/(2*numpy.pi)*60.0*b[i])
        y.append(1000.0*numpy.sin(b[i]))
    
    #Store data    
    pytplot.store_data('sinx', data={'x':x, 'y':y})
    #Apply clip
    pyspedas.xclip('sinx', -850.0, 850.0)
    #Plot
    pytplot.tplot(['sinx','sinx-clip'])
	
#Run the example code
#ex_create()