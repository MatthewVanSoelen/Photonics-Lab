

import tkinter as tk
from imageprocessing import MyImage
from grating_processing import MyGrating

class ListItem():
    """
    Group the image and grating information in one object
    """

    def __init__ (self, image: MyImage, grating: MyGrating, item_details: dict):
        self.image = image
        self.grating = grating
        self.item_details = item_details
        self.image_as_array = []
        self.map_timing = item_details['map_timing']
        self.map_laser_power = item_details['map_laser_power']


        # print(self.image, self.grating, self.item_details)

    def __repr__(self):
        if self.grating.configs['g_type'] == 'Custom':
            name = "%s %s %s" %(self.image.name_image, self.grating.configs['g_type'], self.grating.configs['grating_name'])
        else:
            name = "%s %s %d" %(self.image.name_image, self.grating.configs['g_type'], self.grating.configs['g_angle'])
        return name
    
    def __str__ (self):
        if self.grating.configs['g_type'] == 'Custom':
            name = "%s %s %s" %(self.image.name_image, self.grating.configs['g_type'], self.grating.configs['grating_name'])
        else:
            name = "%s %s %d" %(self.image.name_image, self.grating.configs['g_type'], self.grating.configs['g_angle'])
        return name