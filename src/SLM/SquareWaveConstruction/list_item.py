

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
            name = "%s %s | " %(self.grating.configs['g_type'], self.grating.configs['grating_name']) + "{:.2f}".format( self.grating.configs['exp_time'], "s")
        else:
            name = "%s %s | " %(self.grating.configs['g_type'], self.grating.configs['g_angle']) + "{:.2f}".format( self.grating.configs['exp_time'], "s")
        return name
    
    def __str__ (self):
        if self.grating.configs['g_type'] == 'Custom':
            name = "%s %s | " %(self.grating.configs['g_type'], self.grating.configs['grating_name']) + "{:.2f}".format( self.grating.configs['exp_time'], "s")
        else:
            name = "%s %s | " %(self.grating.configs['g_type'], self.grating.configs['g_angle']) + "{:.2f}".format( self.grating.configs['exp_time'], "s")
        return name