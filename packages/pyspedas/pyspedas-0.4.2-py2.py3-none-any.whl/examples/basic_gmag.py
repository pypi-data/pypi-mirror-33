# -*- coding: utf-8 -*-
"""
file: basic_gmag.py

Desrciption:  
    Basic example with THEMIS GMAG data.
    Downloads THEMIS data from EPO GMAG stations and plots it.

"""

import pyspedas
import pytplot  

# Print the installed version of pyspedas
pyspedas.get_spedas_prefs() 
# Delete any existing pytplot variables
pytplot.del_data()     
# Define list of dates
time_list = ['2010-11-02', '2010-11-02']
# Get a list of EPO gmag stations
sites = pyspedas.gmag_list(group='epo')
#Download gmag files and load into pyspedas variables
d = pyspedas.themis_load_gmag(time_list, sites, 0)
#Download AE index data
d1 = pyspedas.themis_load_gmag(time_list, ['idx'], 0)
#Get a list of loaded sites
sites_loaded = pytplot.tplot_names()

#Subtact mean values    
for station_var in sites_loaded:
    if station_var not in ['thg_idx_al', 'thg_idx_au', 'thg_idx_ae']:
        time, data = pytplot.get_data(station_var)  
        data1 = data - data.mean(axis=0, keepdims=True)
        pytplot.store_data(station_var, data={'x':time, 'y':data1})
#Plot 
pytplot.tplot_options('title', 'EPO GMAG 2009-10-02')    
pytplot.tplot(sites_loaded)
