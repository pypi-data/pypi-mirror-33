# -*- coding: utf-8 -*-
"""
file: spd_prefs.py

Desrciption:  
    loads preferences 

"""

import os

def get_spedas_prefs():
    """Get all the spedas preferences and return a directory"""    
    
    import pyspedas
    dir_path = os.path.abspath(os.path.dirname(pyspedas.__file__))
    fname = os.path.join(dir_path, 'spd_prefs_txt.py')
    print("Preferences file: " + fname )
    
    """Read preferences"""
    with open(fname) as f:
        content = f.readlines()
    content = [x.strip() for x in content] 
    
    """Fill dictionary""" 
    ans_dict = {}
    for line in content:
        if len(line)>2 or line[0]!="#":
            terms = line.split('=')
            terms = [x.strip() for x in terms]
            if len(terms)==2:
                if terms[0]!='' and terms[1]!='':
                    ans_dict[terms[0].replace("'","")] = terms[1].replace("'","")
                
    return ans_dict
            
    