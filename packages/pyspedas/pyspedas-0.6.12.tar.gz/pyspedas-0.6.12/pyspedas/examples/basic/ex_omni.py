# -*- coding: utf-8 -*-
"""
File: 
    ex_omni.py

Desrciption:  
    Basic example of plotting OMNI data.
    
"""

import pyspedas
import pytplot

def ex_omni():
    # Print the installed version of pyspedas
    pyspedas.get_spedas_prefs() 
    # Delete any existing pytplot variables
    pytplot.del_data()     
    # Download THEMIS state data for 2015-12-31
    pyspedas.load_data('omni', '2015-12-31', '', '', '1min')
    pytplot.tplot_options('title', 'omni 2015-12-31') 
    pytplot.tplot(['flow_speed'])

#Run the example code
#ex_omni()