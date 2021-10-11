
import ntpath
from PIL import Image
from PIL import ImageTk
from imageprocessing import MyImage
import numpy as np

from exceptions import InputError
from exceptions import NoFileError
from exceptions import UnknownError

class PatternItem():
    """
        Class to represent a Pattern Item, inlcuding the following data:
        image : PIL.Image
        Folder Path : String
        Pattern Name: String
        id # : Int
        X & Y: Ints - the position the sawtooth pattern cooresponds with in the Fouirer Tranform (FT)
        frequency: Float
        Angle: Float (radians)
        Amplitude: Int - the grayscale value of the point the pattern cooresponds with in the FT

    """
    def __init__(self, file_name, folder_path, id_num, x_pos, y_pos, angle, frequency, amplitude, image):
        self.file_name = file_name
        self.folder_path = folder_path
        self.folder_name = ntpath.basename(self.folder_path)
        self.id_num = id_num
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.angle = angle
        self.frequency = frequency
        self.amplitude = amplitude
        self.image = image
        self.image_tk = ImageTk.PhotoImage(self.image)
        self.tk_preview_image = self.create_tk_preview(self.image)
        print("%s - %sX%s"%(self.file_name, self.tk_preview_image.width(), self.tk_preview_image.height()))


    def create_tk_preview(self, image):

        ratio = 1
        self.max_display_x = 200
        self.max_display_y = 200
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
    
    def downsize_image(self, new_xy:tuple, image_to_mod:Image=None):
            """
            Downsize image, default image is self.image_PIL.
            Returns:
                image : Image.Image : PIL image cropped
            """
            
            image = image_to_mod
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
            
            return image

    def __repr__(self):
        return self.file_name


    def __str__(self):
        return self.file_name

    # def construct(self, file_name, folder_path, id_num, x_pos, y_pos, angle, frequency, amplitude, image):
    #     self.file_name = file_name
    #     self.folder_path = folder_path
    #     self.id_num = id_num
    #     self.x_pos = x_pos
    #     self.y_pos = y_pos
    #     self.angle = angle
    #     self.frequency = frequency
    #     self.amplitude = amplitude
    #     self.image = image