# -*- coding: utf-8 -*-
"""
file: basic_analysis.py

Desrciption:  
    Basic example using analysis functions.
    Downloads THEMIS data and plots it.

"""

import pyspedas
import pytplot

def basic_analysis():
    # Print the installed version of pyspedas
    pyspedas.spd_version()
    # Delete any existing pytplot variables
    pytplot.del_data()     
    # Download THEMIS state data for 2015-12-31
    pyspedas.load_data('themis', '2015-12-31', ['tha'], 'state', 'l1', False)
    # Get data into python variables
    pyspedas.substract_average('tha_vel', '')
    # Plot velocity and velocity-average
    pytplot.tplot(["tha_vel","tha_vel-d"])

#Run the example code
#basic_analysis()