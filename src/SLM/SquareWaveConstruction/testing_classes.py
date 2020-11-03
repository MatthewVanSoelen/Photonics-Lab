# -*- coding: utf-8 -*-
"""
Created on Sat Aug  8 12:16:26 2020

@author: Matthew_VS
"""
import tkinter as tk
from grating_processing import MyGrating

class Test():
    def __init__(self, name, grating: MyGrating):
        self.name = name
        self.grating = grating
        
    def __repr__ (self):
        return "%s %s" %(self.name, self.grating.configs)
        
    def __str__ (self):
        return "%s %s" %(self.name, self.grating.configs)
    
temp = tk.Tk()
grating_configs = {
    'max_display_x':200,
    'max_display_y':200,
    'file_path':'Images/Sampe_Grating.png',
    'grating_name':'Sampe_Grating.png',
    'g_type' : 'SawTooth',
    'g_angle' : 0,
    'y_max' : 255,
    'y_min' : 0,
    'period' : 100,
    'reverse' : 0
    }
myList = []

item = Test("matthew", MyGrating(grating_configs))
myList.append(item)
print(myList)

grating_configs['g_angle'] = 30
item = Test("Emily", MyGrating(grating_configs))
myList.append(item)
print(myList)

grating_configs['g_angle'] = 60
item = Test("John", MyGrating(grating_configs))
myList.append(item)
print(myList)