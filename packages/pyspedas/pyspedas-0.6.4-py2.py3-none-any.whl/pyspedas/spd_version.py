# -*- coding: utf-8 -*-
"""
File: 
    spd_version.py

Desrciption:  
    Pyspedas version number. 
    
Returns:
    The version number for the current installation.

"""

def spd_version(): 
    import os.path
    dir_path = os.path.abspath(os.path.dirname(__file__))
    fname = os.path.join(dir_path, 'spd_prefs_txt.py')
    print("Preferences file: " + fname )     
    
    import pkg_resources
    ver = pkg_resources.get_distribution("pyspedas").version
    print("pyspedas version: " + ver)  