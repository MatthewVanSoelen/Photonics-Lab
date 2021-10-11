

import tkinter as tk
from imageprocessing import MyImage
from grating_processing import MyGrating

class ListItem():
    """
    Group the image and grating information in one object
    """

    def __init__ (self, grating: MyGrating):
        self.grating = grating


        # print(self.image, self.grating, self.item_details)

    def __repr__(self):
            if self.grating.configs['g_type'] == 'Custom':
                name = "%s %s" %(self.grating.configs['g_type'], self.grating.configs['grating_name']) + "\N{DEGREE SIGN} | {:.2f} (s)| {:.2f} (mW)".format( self.grating.configs['exp_time'],self.grating.configs['laser_power'])
            else:
                name = "%s %s" %(self.grating.configs['g_type'], self.grating.configs['g_angle']) + "\N{DEGREE SIGN} | {:.2f} (s)| {:.2f} (mW)".format( self.grating.configs['exp_time'],self.grating.configs['laser_power'])
            return name
    
    def __str__ (self):
            if self.grating.configs['g_type'] == 'Custom':
                name = "%s %s" %(self.grating.configs['g_type'], self.grating.configs['grating_name']) + "\N{DEGREE SIGN} | {:.2f} (s)| {:.2f} (mW)".format( self.grating.configs['exp_time'],self.grating.configs['laser_power'])
            else:
                name = "%s %s" %(self.grating.configs['g_type'], self.grating.configs['g_angle']) + "\N{DEGREE SIGN} | {:.2f} (s)| {:.2f} (mW)".format( self.grating.configs['exp_time'],self.grating.configs['laser_power'])
            return name