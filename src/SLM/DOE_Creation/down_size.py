
import ntpath
from PIL import Image
from PIL import ImageTk
from imageprocessing import MyImage
import numpy as np

def create_tk_preview( image):

    ratio = 1
    max_display_x = 200
    max_display_y = 200
    downsize_for_window = False
    #Determine if image is too wide.
    if image.width >  max_display_x:
        downsize_for_window = True
        #Establish downsize ratio.
        if ratio >  max_display_x / image.width:
            ratio =  max_display_x / image.width
    if image.height >  max_display_y:
        downsize_for_window = True
        #Override downsize ratio if y needs more downsize.
        if ratio >  max_display_y / image.height:
            ratio =  max_display_y / image.height 
    if downsize_for_window:
        #New size should be downsized with same ratio.
        new_x = int(image.width * ratio)
        new_y = int(image.height * ratio)
        image_for_window =  downsize_image((new_x, new_y), image)
    else:
        image_for_window = image
    #Convert to a tkinter PhotoImage and return.

    return image_for_window
    
def downsize_image(new_xy:tuple, image_to_mod:Image=None):
    """
    Downsize image, default image is  image_PIL.
    Returns:
        image : Image.Image : PIL image cropped
    """
    
    image = image_to_mod
    new_x = new_xy[0]
    new_y = new_xy[1]
    image = image.resize(new_xy)
    return image

image = Image.open("/Users/matthewvansoelen/Desktop/Photonics-Lab/src/SLM/Patterns_and_Tools/Experiment_Sim/Pattern_Gui_Data/smile_emoji.png").convert('L')
image = create_tk_preview(image)
image.show()
