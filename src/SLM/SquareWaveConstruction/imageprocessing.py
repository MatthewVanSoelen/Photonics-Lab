"""
Provide image processing across PIL and tkinter libraries.

@author: Luke Kurlandski
@date: December 2019
@copyright: Copyright 2019, Luke Kurlandski, all rights reserved

Special thanks to Daniel Stolz, Matthew Van Soelen, and Dr. David McGee.

Read the Program Guide for detailed information about this program.
"""

from PIL import Image
from PIL import ImageTk
import numpy as np


from exceptions import InputError
from exceptions import NoFileError
from exceptions import UnknownError

class MyImage:

    def __init__(self, configs: dict):
        """
        Create an image object that contains PIL and tkinter images.
        """

        self.max_display_x = (configs['max_display_x'] if 'max_display_x' 
            in configs else 200)
        self.max_display_y = (configs['max_display_y'] if 'max_display_y' 
            in configs else 200)
        self.file_image = (configs['file_image'] if 'file_image' 
            in configs else None)
        self.name_image = (configs['name_image'] if 'name_image' 
            in configs else 'Some Image')
        self.get_images()

    def get_images(self):
        """
        Get and process the images from the file.
        """

        #Get the image from the file and populate the image members.
        try:
            self.original_PIL = Image.open(self.file_image)
        except IOError as e: 
            message = 'The image could not be found:\n\t' + self.file_image
            raise NoFileError(message, e)
        self.modified_PIL = self.original_PIL.convert('L')
        #Downsize tkinter images as needed for display on the main window.
        self.original_tkinter = self.get_window_image(self.original_PIL)
        self.modified_tkinter = self.get_window_image(self.modified_PIL)
        #Get the array representations of the image.
        self.original_array = self.image_as_array(self.original_PIL)
        self.modified_array = self.image_as_array(self.modified_PIL)

    def get_window_image(self, image:Image.Image):
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
        
        image = self.original_PIL.convert('L') if image_to_mod is None else image_to_mod
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

    def crop_image(self, cropping:str, image_to_mod:Image.Image=None):
        """
        Crop image, default image is self.modified_PIL.
        Returns:
            image : Image.Image : PIL image cropped
        """
        
        image = self.modified_PIL if image_to_mod is None else image_to_mod
        #Process the cropping string for x and y coordinates
        if cropping == '': 
            return
        try:
            comma = cropping.find(',')
            brace = cropping.find(')')
            x1 = int(cropping[1:comma])
            y1 = int(cropping[comma+1:brace])
            cropping = cropping[brace+2:]
            comma = cropping.find(',')
            brace = cropping.find(')')
            x2 = int(cropping[1:comma])
            y2 = int(cropping[comma+1:brace])
        except Exception as e: 
            message = 'The cropping string cannot be processed.'
            advice = 'Ensure the format is correct.'
            raise InputError(message, e, advice)
        #Raise exception if input is out of image bounds
        if x1<0 or y1<0 or x1>x2 or y1>y2 or x2>image.width or y2>image.height: 
            message = 'The cropping dimentions are invalid.'
            advice = 'Ensure the dimentions are inside image bounds.'
            raise InputError(message, None, advice)
        #Crop the image
        try:
            image = image.crop((x1,y1,x2,y2))
        except Exception as e:
            message = 'Unknown error occurred cropping the image.'
            raise UnknownError(message, e)
        #Update data members if nessecary.
        if image_to_mod is None:
            self.modified_PIL = image
            self.modified_tkinter = self.get_window_image(image)
            self.modified_array = self.image_as_array(image)
        return image

    def image_as_array(self, image:Image.Image):
        """
        Create an array representation from an image.
        Returns:
            image_list : list[list[int]] : numeric representation of image
        """

        image_array = np.asarray(image)
        image_list = image_array.tolist()
        return image_list



