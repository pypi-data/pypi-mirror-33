# -*- coding: utf-8 -*-
"""
Created on Mon May  7 14:39:30 2018

IDL commands:
thm_load_sst, probe='a', trange=['2015-12-25','2015-12-26'], datatype='*', level='l2'
tplot, 'tha_psif_en_eflux'
makepng,'c:/temp/pyspedas/tha_psif_en_eflux'
 
@author: nikos
"""

import pyspedas
import pytplot

# Print the installed version of pyspedas
pyspedas.get_spedas_prefs() 
# Delete any existing pytplot variables
pytplot.del_data()     
# Download THEMIS state data for 2015-12-31
d = pyspedas.load_data('themis', '2015-12-31', ['tha'], 'sst', 'l2', False)
pytplot.tplot_options('title', 'tha_psif_en_eflux 2015-12-31') 
pytplot.ylim('tha_psif_en_eflux', 10000.0, 10000000.0)
pytplot.options('tha_psif_en_eflux', 'colormap', 'viridis')
pytplot.tplot(['tha_psif_en_eflux'])
