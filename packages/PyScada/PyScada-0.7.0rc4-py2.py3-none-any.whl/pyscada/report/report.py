# -*- coding: utf-8 -*-

import numpy as np

try: 
    from matplotlib import pyplot as plt
    libs_ok = True
except ImportError:
    libs_ok = False
    
    
def save_chart():
    '''
    
    '''
    f1 = plt.figure(figsize=(8, 6),dpi=120)
    plt.title()
    filename = ''
    plt.ylabel()
    plt.xlabel()
    f1.savefig(filename, bbox_inches='tight')


def combiened_chart():
    '''
    
    '''