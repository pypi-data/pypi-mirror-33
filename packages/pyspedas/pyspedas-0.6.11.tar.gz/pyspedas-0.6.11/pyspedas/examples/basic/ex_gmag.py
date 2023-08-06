# -*- coding: utf-8 -*-
"""
File: 
    ex_gmag.py

Desrciption:  
    Basic example with THEMIS GMAG data.
    Downloads THEMIS data from EPO GMAG stations and plots it.

"""

import pyspedas
import pytplot  

def ex_gmag():
    # Print the installed version of pyspedas
    pyspedas.get_spedas_prefs() 
    # Delete any existing pytplot variables
    pytplot.del_data()     
    # Define list of dates
    time_list = ['2015-12-31']
    # Get a list of EPO gmag stations
    sites = pyspedas.gmag_list(group='epo')
    #Download gmag files and load into pyspedas variables
    pyspedas.load_data('gmag', time_list, sites, '', '')
    #Get a list of loaded sites
    sites_loaded = pytplot.tplot_names()    
    #Subtact mean values 
    pyspedas.subtract_average(sites_loaded, '')
    #Download AE index data
    pyspedas.load_data('gmag', time_list, ['idx'], '', '')    
    #Plot 
    sites_loaded = pytplot.tplot_names()
    pytplot.tplot_options('title', 'EPO GMAG 2015-12-31')    
    pytplot.tplot(sites_loaded)

#Run the example code
#ex_gmag()