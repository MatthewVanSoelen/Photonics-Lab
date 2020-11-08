"""
Provide image processing across PIL and tkinter libraries.

@author: Matthew Van Soelen
@date: December 2020
@copyright: Copyright 2020, Luke Kurlandski, all rights reserved

Special thanks to Daniel Stolz, Luke Kurlandski, and Dr. David McGee.

Read the Program Guide for detailed information about this program.
"""

from PIL import Image
from PIL import ImageTk
from imageprocessing import MyImage
import numpy as np

from exceptions import InputError
from exceptions import NoFileError
from exceptions import UnknownError


class MyGrating:
        def __init__(self, configs: dict):
            """
            Creates an grating opject that contains PIL and tkinter images.
            """
            
            self.configs = configs.copy()
            self.max_display_x = (configs['max_display_x'] if 'max_display_x' 
                in configs else 200)
            self.max_display_y = (configs['max_display_y'] if 'max_display_y' 
                in configs else 200)
            self.file_path = (configs['file_path'] if 'file_path'
                in configs else None)
            self.grating_name = (configs['grating_name'] if 'grating_name'
                in configs else 'Some Graitng')
            self.create_grating_image(configs)
            
        def center_crop(self, image, array_width, array_height, width, height):
            x_margin = (array_width - width) //2
            y_margin = (array_height - height) // 2
            
            return image.crop((x_margin, y_margin, x_margin + width, y_margin + height))
            
        def generate_pattern_array(self, height_array, width_array, configs: dict):
            grating_array = np.zeros((height_array, width_array), dtype = np.uint16)
            
            reverse = 0
            if(configs['reverse'] == 0):
                reverse = 1
                y_intercept = configs['y_min']
            else:
                reverse = -1
                y_intercept = configs['y_max']

            if(configs['g_type'] == 'SawTooth'):
                slope = (configs['y_max'] - configs['y_min'])/configs['period']
                for i in range(width_array):                        # for creates color for each column
                    color = slope * reverse * (i % configs['period']) + y_intercept    # Slope intercept form: y = mx + b (y = color)
                    grating_array[:, i] = color

            elif(configs['g_type'] == 'Triangle'):
                period_counter = 0
                period = (configs['period'] / 2)
                slope = (configs['y_max'] - configs['y_min'])/period
                for i in range(width_array):
                    if(i % period == 0):
                        period_counter += 1

                    if(period_counter % 2 == configs['reverse']):
                        color = slope * -1 * (i % period) + configs['y_max']
                    else:
                        color = slope * (i % period) + configs['y_min']
                    grating_array[:, i] = color
            
            elif(configs['g_type'] == 'Circle'):
                cx, cy = width_array //2, height_array //2 # The center of circle
                radius = cy
                slope = (configs['y_max'] - configs['y_min'])/configs['period']
                for i in range(width_array):
                    color = slope * reverse * (i % configs['period']) + y_intercept
                    x, y = np.ogrid[-radius: radius, -radius: radius]
                    index = x**2 + y**2 <= radius**2
                    grating_array[cy-radius:cy+radius, cx-radius:cx+radius][index] = color
                    radius -= 1
                
                    
            return grating_array

        def create_grating_image(self, configs: dict):
            '''

            '''
            width = 1920
            height = 1152

            width_array = int(np.ceil( np.sqrt(pow(width, 2) + pow(height, 2))))
            height_array = width_array
            
            if configs['g_type'] == 'Custom':
                try:
                    self.grating_image = Image.open(self.file_path)
                except:
                    temp = np.zeros((height_array, width_array), dtype = np.uint16)
                    self.grating_image = Image.fromarray(temp)
                    self.grating_image = self.grating_image.convert('L')
                    self.grating_image = self.center_crop(self.grating_image, width_array, height_array, width, height)
                    print("Bad grating file path-%s"%self.file_path)
            else:
                
                self.g_array = self.generate_pattern_array(height_array, width_array, configs)
            
                self.grating_image = Image.fromarray(self.g_array)
            
                self.grating_image = self.grating_image.convert('L')
                self.grating_image = self.grating_image.rotate(configs['g_angle'])
                self.grating_image = self.center_crop(self.grating_image, width_array, height_array, width, height)
            
            self.grating_tk = ImageTk.PhotoImage(self.grating_image)
            self.grating_preview_tk = self.get_grating_preview(self.grating_image)


        def get_grating_preview(self, image:Image.Image):
            """
            Get the modified tkinter image for display on main window.
            Returns:
                image_tk : tk.PhotoImage : image appropriately sized for display
            """

            #Default downsize ratio is 1.
            ratio = 1 
            downsize_for_window = False
            #Determine if image is too wide.
            if image.width > self.max_display_x:
                downsize_for_window = True
                #Establish downsize ratio.
                if ratio > self.max_display_x / image.width:
                    ratio = self.max_display_x / image.width
            if image.height > self.max_display_y:
                downsize_for_window = True
                #Override downsize ratio if y needs more downsize.
                if ratio > self.max_display_y / image.height:
                    ratio = self.max_display_y / image.height 
            if downsize_for_window:
                #New size should be downsized with same ratio.
                new_x = int(image.width * ratio)
                new_y = int(image.height * ratio)
                image_for_window = self.downsize_image((new_x, new_y), image)
            else:
                image_for_window = image
            #Convert to a tkinter PhotoImage and return.
            image_tk = ImageTk.PhotoImage(image_for_window)
            return image_tk

        def downsize_image(self, new_xy:tuple, image_to_mod:Image.Image=None):
            """
            Downsize image, default image is self.image_PIL.
            Returns:
                image : Image.Image : PIL image cropped
            """
            
            image = self.grating_image if image_to_mod is None else image_to_mod
            new_x = new_xy[0]
            new_y = new_xy[1]
            if not isinstance(new_x, int) or not isinstance(new_y, int):
                message = 'Attempting to downsize image with non int dimentions.'
                raise InputError(message)
            #Check the ensure the dimentions are within the image size
            if new_x > image.width: 
                message = 'Attempting to "upsize" the image horizontally.'
                raise InputError(message) 
            if new_y > image.height: 
                message = 'Attempting to "upsize" the image vertically.'
                raise InputError(message) 
            #Modify the image.
            try:
                image = image.resize(new_xy)
            except Exception as e:
                message = 'Unknown error occured downsizing image.'
                raise UnknownError(message, e)
            #Update data members if nessecary.
            if image_to_mod is None:
                self.modified_PIL = image
                self.modified_tkinter = self.get_window_image(image)
                self.modified_array = self.image_as_array(image)
            return image
        

        def __repr__(self):
            if self.configs['g_type'] == 'Custom':
                name = "%s %s | %d" %(self.configs['g_type'], self.configs['grating_name'], self.configs['exp_time'])
            else:
                name = "%s %s | %d" %(self.configs['g_type'], self.configs['g_angle'], self.configs['exp_time'])
            return name
    
        def __str__ (self):
            if self.configs['g_type'] == 'Custom':
                name = "%s %s | %d" %(self.configs['g_type'], self.configs['grating_name'], self.configs['exp_time'])
            else:
                name = "%s %s | %d" %(self.configs['g_type'], self.configs['g_angle'], self.configs['exp_time'])
            return name