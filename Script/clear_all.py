# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 08:10:08 2024

@author: Paolo Castellini
"""

from IPython import get_ipython
import os

def clear_all():
    # Clear all variables
    get_ipython().magic('reset -f')
    # Clear the console
    os.system('cls' if os.name == 'nt' else 'clear')

clear_all()
